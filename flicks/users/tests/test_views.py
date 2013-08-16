from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

from funfactory.urlresolvers import reverse
from mock import ANY, patch
from nose.tools import eq_, ok_
from waffle import Flag

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.models import UserProfile
from flicks.users.tests import UserFactory
from flicks.users.views import Verify
from flicks.videos.models import Vote
from flicks.videos.tests import VideoFactory


class ProfileTests(TestCase):
    def setUp(self):
        super(ProfileTests, self).setUp()
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
                      mailing_list_signup=True, mailing_list_format='html')
        newsletter_subscribe.delay.assert_called_with(self.user.email,
                                                      source_url=ANY,
                                                      format='html')


@patch('flicks.users.views.super', create=True)
class VerifyTests(TestCase):
    def setUp(self):
        super(VerifyTests, self).setUp()
        Flag.objects.create(name='voting', everyone=True)

        self.factory = RequestFactory()
        self.request = self.factory.post('/')
        self.user = UserFactory.create()

        self.request.user = self.user
        SessionMiddleware().process_request(self.request)
        self.verify = Verify(request=self.request)

    def test_login_success_no_key(self, mock_super):
        """If there is no video id in the session, do nothing."""
        response = self.verify.login_success(1, 'asdf', blah='foo')

        login_success = mock_super.return_value.login_success
        eq_(response, login_success.return_value)
        login_success.assert_called_with(1, 'asdf', blah='foo')

    def test_login_success_invalid_video(self, mock_super):
        """If the video ID is invalid, remove the session key and abort."""
        self.request.session['vote_video'] = 'asdf'
        self.verify.login_success()
        ok_('vote_video' not in self.request.session)
        ok_(not Vote.objects.filter(user=self.user).exists())

    def test_login_success_missing_video(self, mock_super):
        """
        If the video ID doesn't match an existing video, remove the session key
        and abort.
        """
        self.request.session['vote_video'] = '99999'
        self.verify.login_success()
        ok_('vote_video' not in self.request.session)
        ok_(not Vote.objects.filter(user=self.user).exists())

    def test_login_success_vote_exists(self, mock_super):
        """
        If the user has already voted for the video, remove the session key and
        do nothing.
        """
        video = VideoFactory.create()
        Vote.objects.create(user=self.user, video=video)
        self.request.session['vote_video'] = unicode(video.id)

        self.verify.login_success()
        ok_('vote_video' not in self.request.session)
        eq_(Vote.objects.filter(user=self.user, video=video).count(), 1)

    def test_login_success_no_vote(self, mock_super):
        """
        If the user hasn't voted for the video, create a vote for it and remove
        the session key.
        """
        video = VideoFactory.create()
        self.request.session['vote_video'] = unicode(video.id)

        self.verify.login_success()
        ok_('vote_video' not in self.request.session)
        eq_(Vote.objects.filter(user=self.user, video=video).count(), 1)

    def test_login_failure_no_key(self, mock_super):
        """If login fails and the user wasn't voting, do nothing."""
        response = self.verify.login_failure(1, 'asdf', foo='bar')

        login_failure = mock_super.return_value.login_failure
        eq_(response, login_failure.return_value)
        login_failure.assert_called_with(1, 'asdf', foo='bar')

    def test_login_failure_with_key(self, mock_super):
        """If the session key for voting exists when login fails, remove it."""
        self.request.session['vote_video'] = '392'
        self.verify.login_failure()
        ok_('vote_video' not in self.request.session)
