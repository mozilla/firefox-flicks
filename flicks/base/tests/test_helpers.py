from datetime import datetime

from mock import patch
from nose.tools import eq_

from flicks.base.helpers import babel_date, babel_number, country_name
from flicks.base.tests import TestCase


class TestHelpers(TestCase):
    def test_babel_date(self):
        date = datetime(2011, 9, 23)
        with self.activate('en-US'):
            eq_(babel_date(date, 'short'), '9/23/11')
            eq_(babel_date(date, 'medium'), 'Sep 23, 2011')

        with self.activate('fr'):
            eq_(babel_date(date, 'short'), '23/09/11')
            eq_(babel_date(date, 'medium'), '23 sept. 2011')

    def test_babel_number(self):
        number = 1000000
        with self.activate('en-US'):
            eq_(babel_number(number), u'1,000,000')

        with self.activate('fr'):
            # \xa0 is a non-breaking space
            eq_(babel_number(number), u'1\xa0000\xa0000')

    @patch('flicks.base.helpers.product_details')
    def test_country_name(self, product_details):
        product_details.get_regions.side_effect = lambda l: {'au': 'test'}
        with self.activate('fr'):
            name = country_name('au')

        eq_(name, 'test')
        product_details.get_regions.assert_called_with('fr')

    @patch('flicks.base.helpers.product_details')
    def test_country_name_es(self, product_details):
        """
        When `es` is passed as the locale, country_name should use `es-ES` as
        the locale for product_details.
        """
        product_details.get_regions.side_effect = lambda l: {'fr': 'test'}
        with self.activate('es'):
            name = country_name('fr')

        eq_(name, 'test')
        product_details.get_regions.assert_called_with('es-ES')
