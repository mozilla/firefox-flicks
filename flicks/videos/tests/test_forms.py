from contextlib import nested

from elasticutils.tests import ESTestCase
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.videos.forms import SearchForm
from flicks.videos.tests import build_video


class SearchFormTests(TestCase, ESTestCase):
    def _videos(self, **kwargs):
        params = {
            'search': '',
            'category': 'all',
            'region': 'all'
        }
        params.update(kwargs)
        f = SearchForm(params)
        return f.videos()

    def setUp(self):
        self.user = self.build_user()

    def test_search(self):
        """Test that basic title searching works."""
        with nested(build_video(self.user, title='Honey badger'),
                    build_video(self.user, title='Lolcats')) as (v1, v2):
            eq_(list(self._videos(search='badger')), [v1])

    def test_category_filter(self):
        """Test that search results can be filtered by category."""
        with nested(build_video(self.user, category='animation'),
                    build_video(self.user, category='psa')) as (v1, v2):
            eq_(list(self._videos(category='psa')), [v2])

    def test_region_filter(self):
        """Test that search results can be filtered by region."""
        with nested(build_video(self.user, region='asia'),
                    build_video(self.user, region='africa')) as (v1, v2):
            eq_(list(self._videos(region='africa')), [v2])

    def test_invalid_search(self):
        """Test that an invalid form will return an empty list."""
        eq_(self._videos(category=''), [])
