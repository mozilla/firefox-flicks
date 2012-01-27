from nose.tools import ok_

from flicks.base.tests import TestCase
from flicks.users.helpers import gravatar_url


class TestGravatars(TestCase):
    def setUp(self):
        # Gravatar hash for this email is b642b4217b34b1e8d3bd915fc65c4452
        self.user = self.build_user('test@test.com')

    def test_basic(self):
        """Passing an email returns the gravatar url for that email."""
        url = gravatar_url('test@test.com')
        ok_('b642b4217b34b1e8d3bd915fc65c4452' in url)

    def test_user(self):
        """Passing a user returns the gravatar url for that user's email."""
        url = gravatar_url(self.user)
        ok_('b642b4217b34b1e8d3bd915fc65c4452' in url)
