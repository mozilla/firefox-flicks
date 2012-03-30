from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCache, TestCase
from flicks.videos.models import Video
from flicks.videos.tests import build_video
from flicks.videos.util import VIEWS_KEY, add_view, cached_viewcount


class AddViewTests(TestCase):
    def setUp(self):
        self.user = self.build_user()
        self.cache = TestCache()
        self.patcher = patch('flicks.videos.util.cache', self.cache)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_store_in_cache(self):
        """The most-up-to-date view count should be in the cache."""
        with build_video(self.user, views=10) as video:
            add_view(video.id)
            eq_(self.cache.get(VIEWS_KEY % video.id), 11)

    def test_video_does_not_exist(self):
        """If the specified video doesn't exist, return None."""
        eq_(add_view(9999999), None)

    def _get_views(self, video):
        """Get the view count for a video from the DB. Avoids using a stale
        count from a model object.
        """
        return Video.objects.filter(pk=video.pk).values()[0]['views']

    def test_store_at_intervals(self):
        """Test that the view count is written to the DB at certain intervals
        based on the view count.
        """
        # Test each pair of (viewcount, # of view per save)
        for viewcount, per_save in [(0, 1), (100, 10)]:
            with build_video(self.user, views=viewcount) as video:
                # Add per_save - 1 views and ensure each time that the DB
                # hasn't been written to.
                for i in range(per_save - 1):
                    add_view(video.id)
                    eq_(self._get_views(video), viewcount)

                # The last view should trigger a write.
                add_view(video.id)
                eq_(self._get_views(video), viewcount + per_save)


class CachedViewcountTests(TestCase):
    def setUp(self):
        self.user = self.build_user()
        self.cache = TestCache()
        self.patcher = patch('flicks.videos.util.cache', self.cache)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_uncached(self):
        """If the view count isn't in the cache, pull it from the database and
        store  it in the cache.
        """
        with build_video(self.user, views=10) as video:
            eq_(self.cache.get(VIEWS_KEY % video.id), None)
            eq_(cached_viewcount(video.id), 10)
            eq_(self.cache.get(VIEWS_KEY % video.id), 10)

    def test_cached(self):
        """If the view count is in the cache, return that count instead of the
        count in the database.
        """
        with build_video(self.user, views=10) as video:
            self.cache.set(VIEWS_KEY % video.id, 12)
            eq_(cached_viewcount(video.id), 12)

    def test_video_does_not_exist(self):
        """If the specified video doesn't exist, return None."""
        eq_(cached_viewcount(999999), None)
