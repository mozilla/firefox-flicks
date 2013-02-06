from mock import patch
from nose.tools import ok_

from flicks.base.tests import TestCase
from flicks.videos.tests import VideoFactory


class Video2013Tests(TestCase):
    @patch('flicks.videos.models.vimeo')
    @patch('flicks.videos.models.send_approval_email')
    def test_save_approved_not_notified(self, send_approval_email, vimeo):
        """
        If a video being saved is approved, reset the privacy on vimeo to
        'anybody', and if the user hasn't been notified, send an approval email.
        """
        video = VideoFactory.create(approved=False, user_notified=False)
        vimeo.set_privacy.delay.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.delay.called)
        ok_(not send_approval_email.called)

        video.approved = True
        video.save()
        vimeo.set_privacy.delay.assert_called_with(video.vimeo_id, 'anybody')
        send_approval_email.assert_called_with(video)

    @patch('flicks.videos.models.vimeo')
    @patch('flicks.videos.models.send_approval_email')
    def test_save_approved_notified(self, send_approval_email, vimeo):
        """
        If a video being saved is approved, reset the privacy on vimeo to
        'anyone', and if the user has already been notified, don't send a new
        email.
        """
        video = VideoFactory.create(user__email='blah@test.com', approved=False,
                                    user_notified=True)
        vimeo.set_privacy.delay.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.delay.called)
        ok_(not send_approval_email.called)

        video.approved = True
        video.save()
        vimeo.set_privacy.delay.assert_called_with(video.vimeo_id, 'anybody')
        ok_(not send_approval_email.called)

    @patch('flicks.videos.models.vimeo')
    @patch('flicks.videos.models.send_approval_email')
    def test_save_unapproved(self, send_approval_email, vimeo):
        """
        If a video being saved is notapproved, reset the privacy on vimeo to
        'password'.
        """
        video = VideoFactory.create(user__email='blah@test.com', approved=True)
        vimeo.set_privacy.delay.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.delay.called)
        ok_(not send_approval_email.called)

        video.approved = False
        with self.settings(VIMEO_VIDEO_PASSWORD='testpass'):
            video.save()
        vimeo.set_privacy.delay.assert_called_with(video.vimeo_id, 'password',
                                                   password='testpass')
        ok_(not send_approval_email.called)
