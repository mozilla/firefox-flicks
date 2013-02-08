from mock import patch
from nose.tools import ok_

from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos.models import Video
from flicks.videos.tests import VideoFactory


class Video2013Tests(TestCase):
    @patch('flicks.videos.models.process_approval')
    def test_save_process_new(self, process_approval):
        """Trigger the process_approval task if the video is new."""
        user = UserProfileFactory.create().user
        video = VideoFactory.build(title='blahtest', user=user)

        process_approval.delay.reset_mock()
        ok_(not process_approval.delay.called)
        video.save()
        video = Video.objects.get(title='blahtest')
        process_approval.delay.assert_called_with(video.id)

    @patch('flicks.videos.models.process_approval')
    def test_save_process_changed(self, process_approval):
        """Trigger the process_approval task if the approval status changed."""
        video = VideoFactory.create(approved=False)

        process_approval.delay.reset_mock()
        ok_(not process_approval.delay.called)
        video.approved = True
        video.save()
        process_approval.delay.assert_called_with(video.id)

        process_approval.delay.reset_mock()
        ok_(not process_approval.delay.called)
        video.approved = False
        video.save()
        process_approval.delay.assert_called_with(video.id)

    @patch('flicks.videos.models.process_approval')
    def test_save_noprocess_old(self, process_approval):
        """
        Do not rigger the process_approval task if the approval status did not
        change.
        """
        video = VideoFactory.create(approved=False)

        process_approval.delay.reset_mock()
        ok_(not process_approval.delay.called)
        video.title = 'new_title'
        video.save()
        ok_(not process_approval.delay.called)
