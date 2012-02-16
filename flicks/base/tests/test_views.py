from funfactory.urlresolvers import reverse
from nose.tools import eq_

from flicks.base.tests import TestCase


class HomeTests(TestCase):
    def _get(self):
        with self.activate('en-US'):
            return self.client.get(reverse('flicks.base.home'))

    def test_home_redirect(self):
        """If the current user isn't logged in, show the homepage. If they are,
        redirect them to the recent videos page.
        """
        # Test not logged in
        response = self._get()
        eq_(response.status_code, 200)

        # Test logged in
        self.build_user(login=True)
        response = self._get()
        eq_(response.status_code, 302)
        self.assert_viewname_url(response['Location'], 'flicks.videos.recent')
