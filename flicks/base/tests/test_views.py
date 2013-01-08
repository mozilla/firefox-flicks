from django.utils.unittest import skip

from funfactory.urlresolvers import reverse
from nose.tools import eq_

from flicks.base.tests import TestCase


@skip
class HomeTests(TestCase):
    def _get(self):
        with self.activate('en-US'):
            return self.client.get(reverse('flicks.videos.recent'))

    def test_home_redirect(self):
        """If the current user isn't logged in, show the recent videos page.
        If they are, also validate that land on the recent videos page.
        """
        # Test not logged in
        response = self._get()
        eq_(response.status_code, 200)

        # Test logged in
        self.build_user(login=True)
        response = self._get()
        eq_(response.status_code, 200)
