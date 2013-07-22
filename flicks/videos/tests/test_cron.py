from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.videos.cron import update_random_video_ordering
from flicks.videos.models import Video
from flicks.videos.tests import VideoFactory


class UpdateRandomVideoOrderingTests(TestCase):
    @patch('flicks.videos.cron.Video')
    def test_basic(self, MockVideo):
        v1 = VideoFactory.create()
        v2 = VideoFactory.create(random_ordering=5)
        v3 = VideoFactory.create()
        v4 = VideoFactory.create(random_ordering=3)
        MockVideo.objects.order_by.return_value = [v2, v3, v1, v4]

        update_random_video_ordering()
        eq_(list(Video.objects.order_by('random_ordering')), [v2, v3, v1, v4])
