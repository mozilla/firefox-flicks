from nose.tools import eq_

from flicks.base import regions
from flicks.base.tests import TestCase


class TestGetRegion(TestCase):
    def test_basic(self):
        eq_(regions.get_region('us'), regions.NORTH_AMERICA)
        eq_(regions.get_region('gb'), regions.EMEA)
        eq_(regions.get_region('br'), regions.LATIN_AMERICA)
        eq_(regions.get_region('au'), regions.APAC)

    def test_not_found(self):
        eq_(regions.get_region('invalid'), None)
