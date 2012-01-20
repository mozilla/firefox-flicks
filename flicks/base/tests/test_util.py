from django.conf import settings

from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.base.util import absolutify


@patch.object(settings, 'SITE_URL', 'http://test.com')
class AbsolutifyTests(TestCase):
    def test_basic(self):
        """Test that the domain is added correctly."""
        eq_(absolutify('test'), 'http://test.com/test')

    def test_with_slash(self):
        """A path starting with a slash does not have an extra slash."""
        eq_(absolutify('/test/path'), 'http://test.com/test/path')
