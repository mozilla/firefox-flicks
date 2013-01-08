from django.utils.unittest import skip

from funfactory.urlresolvers import reverse
from nose.tools import eq_

from flicks.base.tests import TestCase


@skip
class ProfileRequiredTests(TestCase):
    urls = 'flicks.users.tests.urls'

    def _get(self):
        with self.activate('en-US'):
            response = self.client.get(reverse('profile_view'))
        return response

    def test_no_profile(self):
        """If the user has no profile, redirect them to
        flicks.users.edit_profile.
        """
        self.build_user(salt='no_profile', login=True, profile=False)
        response = self._get()
        eq_(response.status_code, 302)

        self.assert_viewname_url(response['Location'],
                                 'flicks.users.edit_profile')

    def test_has_profile(self):
        """If the user has a profile, let the view run normally."""
        self.build_user(salt='has_profile', login=True)
        response = self._get()
        eq_(response.status_code, 200)
        eq_(response.content, 'test')
