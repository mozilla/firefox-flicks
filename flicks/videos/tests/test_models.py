from mock import ANY, Mock, patch
from nose.tools import eq_, ok_
from requests.exceptions import RequestException

from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos.models import Video2013
from flicks.videos.tests import Video2013Factory
from flicks.videos.vimeo import VimeoServiceError


class Video2013Tests(TestCase):
    @patch('flicks.videos.models.send_approval_email')
    def test_save_process_new(self, send_approval_email):
        """
        Do not call process_approval or send_approval_email if the video is new.
        """
        user = UserProfileFactory.create().user
        video = Video2013Factory.build(title='blahtest', user=user)
        video.process_approval = Mock()
        video.save()

        ok_(not video.process_approval.called)
        ok_(not send_approval_email.called)

    def test_save_process_changed(self):
        """Call process_approval if the approval status changed."""
        video = Video2013Factory.create(approved=False)
        video.process_approval = Mock()

        video.approved = True
        video.save()
        video.process_approval.assert_called_with()

        video.process_approval.reset_mock()
        ok_(not video.process_approval.called)
        video.approved = False
        video.save()
        video.process_approval.assert_called_with()

    def test_save_noprocess_old(self):
        """
        Do not call process_approval if the approval status did not change.
        """
        video = Video2013Factory.create(approved=False)
        video.process_approval = Mock()

        video.title = 'new_title'
        video.save()
        ok_(not video.process_approval.called)

    def test_save_unapproved_no_email(self):
        """If the video is not approved, do not call send_approval_email."""
        video = Video2013Factory.create(approved=True)
        video.user_notified = False
        video.approved = False

        path = 'flicks.videos.models.send_approval_email'
        with patch(path) as send_approval_email:
            video.save()
            ok_(not send_approval_email.called)

    @patch('flicks.videos.models.send_approval_email')
    def test_save_approved_notified_no_email(self, send_approval_email):
        """
        If the video is approved and the user has already been notified, do not
        call send_approval_email.
        """
        video = Video2013Factory.create(approved=False, user_notified=True)
        eq_(video.user_notified, True)
        video.approved = True
        video.save()

        ok_(not send_approval_email.called)

    @patch('flicks.videos.models.send_approval_email')
    def test_save_approved_not_notified(self, send_approval_email):
        """
        If the video is approved and the user hasn't been notified, call
        send_approval_email and update user_notified.
        """
        video = Video2013Factory.create(approved=False, user_notified=False)
        eq_(video.user_notified, False)
        video.approved = True
        video.save()

        video = Video2013.objects.get(id=video.id)
        send_approval_email.assert_called_with(video)
        ok_(video.user_notified)

    @patch('flicks.videos.models.process_deletion')
    def test_delete_process(self, process_deletion):
        """
        When a video is deleted, the process_deletion task should be triggered.
        """
        user = UserProfileFactory.create().user
        video = Video2013Factory.create(user=user, vimeo_id=123456)
        ok_(not process_deletion.delay.called)

        video.delete()
        process_deletion.delay.assert_called_with(123456, user.id)

    @patch('flicks.videos.models.vimeo')
    def test_process_approval(self, vimeo):
        """
        If the video is approved, download the thumbnails and reset the privacy
        on vimeo to 'anybody'.
        """
        video = Video2013Factory.build(approved=True, user_notified=False)
        video.download_thumbnail = Mock()
        video.process_approval()

        video.download_thumbnail.assert_called_with(commit=False)
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'anybody')

    @patch('flicks.videos.models.vimeo')
    def test_process_approval_unapproved(self, vimeo):
        """
        If the video is not approved, reset the privacy on vimeo to 'password'.
        """
        video = Video2013Factory.build(approved=False)
        video.download_thumbnail = Mock()

        with self.settings(VIMEO_VIDEO_PASSWORD='testpass'):
            video.process_approval()
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'password',
                                             password='testpass')

    @patch('flicks.videos.models.vimeo')
    def test_process_approval_thumbnail_fail(self, vimeo):
        """
        If a video is approved but downloading thumbnails has failed, continue
        processing the video approval.
        """
        video = Video2013Factory.build(approved=True, user_notified=False)
        video.download_thumbnail = Mock()
        video.download_thumbnail.side_effect = RequestException
        video.process_approval()

        video.download_thumbnail.assert_called_with(commit=False)
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'anybody')

    @patch('flicks.videos.models.vimeo')
    @patch('flicks.videos.models.requests')
    def test_download_thumbnail(self, requests, vimeo):
        video = Video2013Factory.build()
        video.thumbnail = Mock()
        video.save = Mock()

        vimeo.get_thumbnail_urls.return_value = [
            {'height': '250', '_content': 'http://example.com/qwer.png'},
            {'height': '150', '_content': 'http://example.com/asdf.png'},
            {'height': '80', '_content': 'http://example.com/zxcv.png'},
        ]
        requests.get.return_value = Mock(content='asdf',
                                         url='http://example.com/asdf.png')

        video.download_thumbnail()
        requests.get.assert_called_with('http://example.com/asdf.png')
        video.thumbnail.save.assert_called_with('asdf.png', ANY, save=False)
        video.save.assert_called_with()

    @patch('flicks.videos.models.vimeo')
    def test_download_thumbnail_error(self, vimeo):
        """If no medium-sized thumbnail is found, raise a VimeoServiceError."""
        video = Video2013Factory.build()
        vimeo.get_thumbnail_urls.return_value = [
            {'height': '250', '_content': 'http://example.com/qwer.png'},
            {'height': '80', '_content': 'http://example.com/zxcv.png'},
        ]
        vimeo.VimeoServiceError = VimeoServiceError

        with self.assertRaises(VimeoServiceError):
            video.download_thumbnail()

    @patch('flicks.videos.models.vimeo')
    @patch('flicks.videos.models.requests')
    def test_commit(self, requests, vimeo):
        """If commit is False, do not save the video."""
        video = Video2013Factory.build()
        video.save = Mock()

        vimeo.get_thumbnail_urls.return_value = [
            {'height': '250', '_content': 'http://example.com/qwer.png'},
            {'height': '150', '_content': 'http://example.com/asdf.png'},
            {'height': '80', '_content': 'http://example.com/zxcv.png'},
        ]
        requests.get.return_value = Mock(content='asdf',
                                         url='http://example.com/asdf.png')

        video.download_thumbnail(commit=False)
        ok_(not video.save.called)
