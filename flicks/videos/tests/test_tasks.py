from django.utils.unittest import skip

from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.videos.models import Video
from flicks.videos.tasks import add_vote, send_video_to_vidly
from flicks.videos.tests import build_video


@skip
class SendVideoToVidlyTests(TestCase):
    def _send(self, video, return_value):
        with patch('flicks.videos.tasks.addMedia') as addMedia:
            addMedia.return_value = return_value
            send_video_to_vidly(video)

        video = Video.objects.get(pk=video.pk)
        return video

    def setUp(self):
        self.user = self.build_user()

    def test_error(self):
        """If there's an error, the video's state should change to error."""
        with build_video(self.user) as video:
            video = self._send(video, None)
            eq_(video.state, 'error')

    def test_success(self):
        """A successful upload should mark the video as pending."""
        with build_video(self.user, shortlink='') as video:
            eq_(video.shortlink, '')
            video = self._send(video, 'asdf')
            eq_(video.shortlink, 'asdf')
            eq_(video.state, 'pending')


class AddVotesTests(TestCase):
    def setUp(self):
        self.user = self.build_user()

    def test_basic(self):
        """Calling add_vote increases the vote count."""
        with build_video(self.user, votes=0) as video:
            votes = video.votes
            add_vote(video)
            video = Video.objects.get(pk=video.pk)
            eq_(video.votes, votes + 1)
