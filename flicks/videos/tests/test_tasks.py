from mock import patch
from nose.tools import ok_

from flicks.base import regions
from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos import vimeo
from flicks.videos.tasks import process_video
from flicks.videos.tests import VideoFactory


@patch('flicks.videos.tasks.vimeo')
class TestProcessVideo(TestCase):
    def test_no_video(self, mock_vimeo):
        """If no video is found with the given id, do nothing."""
        process_video(1387589156831)
        ok_(not mock_vimeo.setTitle.called)
        ok_(not mock_vimeo.setDescription.called)
        ok_(not mock_vimeo.addToChannel.called)
        ok_(not mock_vimeo.addTags.called)

    def test_valid_video(self, mock_vimeo):
        """If a valid video id is given, update the Vimeo metadata."""
        user = UserProfileFactory.create(nickname='name', country='us').user
        video = VideoFactory.create(user=user, title='blah', description='asdf',
                                    vimeo_id=7)

        with self.settings(VIMEO_REGION_CHANNELS={regions.NORTH_AMERICA: 18}):
            process_video(video.id)

        mock_vimeo.setTitle.assert_called_with(7, 'blah')
        mock_vimeo.setDescription.assert_called_with(7, 'blah by name\n\nasdf')
        mock_vimeo.addToChannel.assert_called_with(7, 18)
        mock_vimeo.addTags.assert_called_with(7, ['us'])

    @patch('flicks.videos.tasks.process_video.retry', wraps=process_video.retry)
    def test_retry(self, retry, mock_vimeo):
        """
        If a vimeo command fails due to a VimeoServiceError, raise a retry
        exception for celery to retry later.
        """
        mock_vimeo.setTitle.side_effect = vimeo.VimeoServiceError
        mock_vimeo.VimeoServiceError = vimeo.VimeoServiceError
        video = VideoFactory.create()
        ok_(not retry.called)

        # When not being executed in a worker, retry just raises the exception.
        with self.assertRaises(vimeo.VimeoServiceError):
            process_video(video.id)
        ok_(retry.called)
