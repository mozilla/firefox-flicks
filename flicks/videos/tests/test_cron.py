from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCache, TestCase
from flicks.videos.cron import persist_viewcounts
from flicks.videos.models import Video
from flicks.videos.tests import build_video
from flicks.videos.util import VIEWS_KEY

cache = TestCache()


@patch('flicks.videos.cron.cache', cache)
class PersistViewCountsTest(TestCase):
    def setUp(self):
        self.user = self.build_user()
        cache.clear()

    def test_no_videos(self):
        """Test that the cron doesn't fail with no videos."""
        Video.objects.all().delete()
        persist_viewcounts()

    def test_viewcount_updated(self):
        """Test that videos with viewcounts in the cache are updated."""
        with build_video(self.user, views=10) as video:
            cache.set(VIEWS_KEY % video.id, 14)
            eq_(Video.objects.get(id=video.id).views, 10)
            persist_viewcounts()
            eq_(Video.objects.get(id=video.id).views, 14)

    def test_viewcount_unmodified(self):
        """Test that videos without viewcounts in the cache are not updated."""
        with build_video(self.user, views=10) as video:
            eq_(Video.objects.get(id=video.id).views, 10)
            persist_viewcounts()
            eq_(Video.objects.get(id=video.id).views, 10)
