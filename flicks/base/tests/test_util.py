from django.conf import settings

import product_details
from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.base.util import (absolutify, country_choices, get_object_or_none,
                              promo_video_shortlink, redirect)
from flicks.videos.models import Video2012
from flicks.videos.tests import Video2012Factory


@patch.object(settings, 'SITE_URL', 'http://test.com')
class AbsolutifyTests(TestCase):
    def test_basic(self):
        """Test that the domain is added correctly."""
        eq_(absolutify('test'), 'http://test.com/test')

    def test_with_slash(self):
        """A path starting with a slash does not have an extra slash."""
        eq_(absolutify('/test/path'), 'http://test.com/test/path')


class TestRedirect(TestCase):
    urls = 'flicks.base.tests.urls'

    def test_basic(self):
        with self.activate('en-US'):
            response = redirect('mock_view')
        eq_(response.status_code, 302)
        eq_(response['Location'], '/en-US/mock_view')

    def test_permanent(self):
        with self.activate('en-US'):
            response = redirect('mock_view', permanent=True)
        eq_(response.status_code, 301)
        eq_(response['Location'], '/en-US/mock_view')


class TestGetObjectOrNone(TestCase):
    def test_does_not_exist(self):
        """Return None if no matching video exists."""
        value = get_object_or_none(Video2012, title='Does not exist')
        eq_(value, None)

    def test_multiple_objects_returned(self):
        """Return None if multiple objects are returned."""
        Video2012Factory.create(title='multiple')
        Video2012Factory.create(title='multiple')
        value = get_object_or_none(Video2012, title='multiple')
        eq_(value, None)

    def test_exists(self):
        """If no exceptions occur, return the matched object."""
        video = Video2012Factory.create(title='exists')
        value = get_object_or_none(Video2012, title='exists')
        eq_(value, video)


promo_videos = {
    'noir': {
        'en-us': 'english',
        'fr': 'french'
    },
    'no-en-us': {
        'fr': 'french'
    }
}


@patch.object(settings, 'PROMO_VIDEOS', promo_videos)
class TestPromoVideoShortlin(TestCase):
    def test_invalid_promo(self):
        """If an invalid promo name is given, return None."""
        eq_(promo_video_shortlink('invalid'), None)

    def test_no_locale(self):
        """If there is no video matching the current locale, default to
        en-US.
        """
        with self.activate('es'):
            eq_(promo_video_shortlink('noir'), 'english')

    def test_no_en_us(self):
        """If there is no video matching the current locale or en-US,
        return None.
        """
        with self.activate('es'):
            eq_(promo_video_shortlink('no-en-us'), None)

    def test_success(self):
        """If a video for the current locale exists, return it's shortlink."""
        with self.activate('fr'):
            eq_(promo_video_shortlink('noir'), 'french')


@patch.object(product_details, 'product_details')
class CountryChoicesTests(TestCase):
    def test_basic(self, product_details):
        product_details.get_regions.return_value = ({'us': 'United States',
                                                     'fr': 'France'})
        with self.settings(INELIGIBLE_COUNTRIES=['fr']):
            with self.activate('en-US'):
                choices = country_choices(allow_empty=True)

        eq_(choices, [('', '---'), ('us', 'United States')])
        product_details.get_regions.assert_called_with('en-us')

    def test_dont_allow_empty(self, product_details):
        product_details.get_regions.return_value = ({'us': 'United States',
                                                     'fr': 'France'})
        with self.settings(INELIGIBLE_COUNTRIES=['us']):
            with self.activate('fr'):
                choices = country_choices(allow_empty=False)

        eq_(choices, [('fr', 'France')])
        product_details.get_regions.assert_called_with('fr')

