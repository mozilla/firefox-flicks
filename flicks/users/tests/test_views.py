from funfactory.urlresolvers import reverse
from mock import ANY, patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.models import UserProfile
from flicks.users.tests import UserFactory


class TestProfile(TestCase):
    def setUp(self):
        super(TestProfile, self).setUp()
        self.user = UserFactory.create()
        self.browserid_login(self.user.email)

    def _profile(self, method, locale='en-US', **kwargs):
        with self.activate(locale):
            func = self.client.post if method == 'post' else self.client.get
            response = func(reverse('flicks.users.profile'), kwargs)
        return response

    def test_get(self):
        """Render 'users/profile.html' on GET."""
        response = self._profile('get')
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_post_invalid(self):
        """
        If POSTed with invalid values, render the form again and do not create
        a profile.
        """
        response = self._profile('post', full_name='blah',
                                 privacy_policy_agree=False)
        self.assertTemplateUsed(response, 'users/profile.html')
        ok_(not UserProfile.objects.filter(user=self.user).exists())

    def test_post_valid(self):
        """
        If POSTed with valid values, create a profile and redirect to
        flicks.videos.upload.
        """
        response = self._profile('post', locale='fr', full_name='blah',
                                 nickname='blah', country='fr',
                                 privacy_policy_agree=True)
        redirects_(response, 'flicks.videos.upload', locale='fr')
        ok_(UserProfile.objects.filter(user=self.user).exists())
        eq_(UserProfile.objects.get(user=self.user).locale, 'fr')

    @patch('flicks.users.views.newsletter_subscribe')
    def test_mailing_list_signup(self, newsletter_subscribe):
        """
        If the user has checked the mailing_list_signup checkbox, trigger the
        newsletter_subscribe task.
        """
        self._profile('post', locale='fr', full_name='blah', nickname='blah',
                      country='fr', privacy_policy_agree=True,
                      mailing_list_signup=True)
        newsletter_subscribe.delay.assert_called_with(self.user.email,
                                                      source_url=ANY)
