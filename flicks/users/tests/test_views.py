from contextlib import nested

from django.conf import settings
from django.utils.unittest import skip

from funfactory.urlresolvers import reverse
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.users.models import UserProfile
from flicks.users.tests import mock_browserid


@skip
class VerifyTests(TestCase):
    def _post(self, email, assertion='asdf'):
        with nested(self.activate('en-US'), mock_browserid(email)):
            response = self.client.post(reverse('flicks.users.verify'),
                                        {'assertion': assertion})

        return response

    def test_invalid_form(self):
        """If no assertion is provided, redirect to the login failure page."""
        response = self._post(None, None)
        eq_(response.status_code, 302)
        self.assert_viewname_url(response['Location'],
                                 settings.LOGIN_REDIRECT_FAILURE)

    def test_auth_failure(self):
        """If the user does not successfully auth, redirect to the login
        failure page.
        """
        response = self._post(None)
        eq_(response.status_code, 302)
        self.assert_viewname_url(response['Location'],
                                 settings.LOGIN_REDIRECT_FAILURE)

    def test_no_profile(self):
        """If the user auths and has no profile, redirect to the create
        profile page.
        """
        self.build_user(email='verify.no.profile@test.com', profile=False)
        response = self._post('verify.no.profile@test.com')
        eq_(response.status_code, 302)
        self.assert_viewname_url(response['Location'],
                                 'flicks.users.edit_profile')

    def test_has_profile(self):
        """If the user auths and has a profile, redirect to LOGIN_REDIRECT."""
        self.build_user(email='verify.has.profile@test.com', profile=True)
        response = self._post('verify.has.profile@test.com')
        eq_(response.status_code, 302)
        self.assert_viewname_url(response['Location'], settings.LOGIN_REDIRECT)


@skip
class EditProfileTests(TestCase):
    def _post(self, **kwargs):
        with self.activate('en-US'):
            response = self.client.post(reverse('flicks.users.edit_profile'),
                                        kwargs)
        return response

    def test_no_profile(self):
        """If the user has no profile, a new one is created."""
        user = self.build_user(salt='no.profile', login=True, profile=False)
        eq_(UserProfile.objects.filter(pk=user.pk).exists(), False)

        self._post(bio='asdf', full_name='bob', agreement='on')
        eq_(UserProfile.objects.filter(pk=user.pk).exists(), True)

    def test_has_profile(self):
        """If the user has a profile, it is edited."""
        user = self.build_user(salt='has.profile', login=True)
        user.userprofile.full_name = 'bob'
        user.userprofile.bio = 'asdf'
        user.userprofile.save()

        profile = UserProfile.objects.get(pk=user.pk)
        eq_(profile.bio, 'asdf')

        self._post(bio='1234', full_name='bob', agreement='on')
        profile = UserProfile.objects.get(pk=user.pk)
        eq_(profile.bio, '1234')


@skip
class DetailsTests(TestCase):
    def _get(self, user_id):
        with self.activate('en-US'):
            response = self.client.get(reverse('flicks.users.details',
                                               kwargs={'user_id': user_id}))
        return response

    def test_no_profile_404(self):
        """If the requested user has no profile, return a 404."""
        user = self.build_user(salt='no.profile', profile=False)
        response = self._get(user.id)
        eq_(response.status_code, 404)
