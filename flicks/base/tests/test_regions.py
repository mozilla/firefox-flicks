from mock import patch
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


@patch('flicks.base.regions.regions', {1: ['us', 'fr'], 2: ['ws']})
class TestGetCountries(TestCase):
    def test_basic(self):
        eq_(regions.get_countries(1), ['us', 'fr'])
        eq_(regions.get_countries('1'), ['us', 'fr'])
        eq_(regions.get_countries(2), ['ws'])
        eq_(regions.get_countries('2'), ['ws'])

    def test_error(self):
        eq_(regions.get_countries(7), None)
        eq_(regions.get_countries('7'), None)
        eq_(regions.get_countries('not a number'), None)
        eq_(regions.get_countries(False), None)
