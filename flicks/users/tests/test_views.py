from funfactory.urlresolvers import reverse
from nose.tools import ok_

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.models import UserProfile
from flicks.users.tests import UserFactory


class TestProfile(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.browserid_login(self.user.email)

    def _profile(self, method, **kwargs):
        with self.activate('en-US'):
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
        response = self._profile('post', full_name='blah', nickname='blah',
                                 country='us', privacy_policy_agree=True)
        redirects_(response, 'flicks.videos.upload')
        ok_(UserProfile.objects.filter(user=self.user).exists())
