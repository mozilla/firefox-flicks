from django.contrib.auth.models import Permission

from mock import ANY, patch
from nose.tools import eq_, ok_

from flicks.base import regions
from flicks.base.tests import TestCase
from flicks.base.tests.tools import CONTAINS
from flicks.users.tests import GroupFactory, UserFactory, UserProfileFactory

from flicks.videos.models import Video
from flicks.videos.tasks import process_approval, process_video
from flicks.videos.tests import VideoFactory


@patch('flicks.videos.tasks.vimeo')
class TestProcessVideo(TestCase):
    def test_no_video(self, mock_vimeo):
        """If no video is found with the given id, do nothing."""
        process_video(1387589156831)
        ok_(not mock_vimeo.set_title.called)
        ok_(not mock_vimeo.set_description.called)
        ok_(not mock_vimeo.add_to_channel.called)
        ok_(not mock_vimeo.add_tags.called)

    @patch('flicks.videos.tasks.send_mail')
    def test_valid_video(self, send_mail, mock_vimeo):
        """If a valid video id is given, update the Vimeo metadata."""
        # Many to many makes this super-verbose. Essentially, create two
        # moderators, one who is part of a moderator group and the other who
        # has the change_video2013 permission directly.
        perm = Permission.objects.get(codename='change_video2013')
        group = GroupFactory()
        group.permissions = [perm]
        group.save()
        moderator1 = UserFactory(email='test1@test.com')
        moderator1.user_permissions = [perm]
        moderator1.save()
        moderator2 = UserFactory.create(email='test2@test.com')
        moderator2.groups = [group]
        moderator2.save()

        user = UserProfileFactory.create(nickname='name', country='us').user
        video = VideoFactory.create(user=user, title='blah', description='asdf',
                                    vimeo_id=7)

        with self.settings(VIMEO_REGION_CHANNELS={regions.NORTH_AMERICA: 18},
                           DEFAULT_FROM_EMAIL='blah@test.com'):
            process_video(video.id)

        mock_vimeo.set_title.assert_called_with(7, 'blah')
        mock_vimeo.set_description.assert_called_with(7, 'blah by name\n\nasdf')
        mock_vimeo.add_to_channel.assert_called_with(7, 18)
        mock_vimeo.add_tags.assert_called_with(7, ['us'])

        send_mail.assert_called_with(ANY, ANY, 'blah@test.com',
                                     CONTAINS('test1@test.com',
                                              'test2@test.com'))


class ProcessApprovalTests(TestCase):
    @patch('flicks.videos.tasks.vimeo')
    @patch('flicks.videos.tasks.send_approval_email')
    def test_approved_not_notified(self, send_approval_email, vimeo):
        """
        If the video is approved, reset the privacy on vimeo to 'anybody',
        and if the user hasn't been notified, send an approval email.
        """
        video = VideoFactory.create(approved=True, user_notified=False)
        vimeo.set_privacy.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.called)
        ok_(not send_approval_email.called)

        process_approval(video.id)
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'anybody')
        send_approval_email.assert_called_with(video)

    @patch('flicks.videos.tasks.vimeo')
    @patch('flicks.videos.tasks.send_approval_email')
    def test_approved_notified(self, send_approval_email, vimeo):
        """
        If the video is approved, reset the privacy on vimeo to 'anybody', and
        if the user has already been notified, don't send a new email.
        """
        video = VideoFactory.create(user__email='blah@test.com', approved=True,
                                    user_notified=True)
        vimeo.set_privacy.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.called)
        ok_(not send_approval_email.called)

        process_approval(video.id)
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'anybody')
        ok_(not send_approval_email.called)

    @patch('flicks.videos.tasks.vimeo')
    @patch('flicks.videos.tasks.send_approval_email')
    def test_unapproved(self, send_approval_email, vimeo):
        """
        If the video is not approved, reset the privacy on vimeo to 'password'.
        """
        video = VideoFactory.create(user__email='blah@test.com', approved=False)
        vimeo.set_privacy.reset_mock()
        send_approval_email.reset_mock()
        ok_(not vimeo.set_privacy.called)
        ok_(not send_approval_email.called)

        with self.settings(VIMEO_VIDEO_PASSWORD='testpass'):
            process_approval(video.id)
        vimeo.set_privacy.assert_called_with(video.vimeo_id, 'password',
                                                   password='testpass')
        ok_(not send_approval_email.called)

    @patch('flicks.videos.tasks.vimeo')
    def test_thumbnails(self, vimeo):
        """If a video is approved, pull the latest thumbnails from Vimeo."""
        vimeo.get_thumbnail_urls.return_value = [
            {'height': '75', '_content': 'http://test1.com'},
            {'height': '150', '_content': 'http://test2.com'},
            {'height': '480', '_content': 'http://test3.com'},
            {'height': '7532', '_content': 'http://test4.com'},
        ]

        video = VideoFactory.create(approved=True)
        vimeo.get_thumbnail_urls.reset_mock()
        ok_(not vimeo.get_thumbnail_urls.called)

        process_approval(video.id)

        vimeo.get_thumbnail_urls.assert_called_with(video.vimeo_id)
        video = Video.objects.get(id=video.id)
        eq_(video.small_thumbnail_url, 'http://test1.com')
        eq_(video.medium_thumbnail_url, 'http://test2.com')
        eq_(video.large_thumbnail_url, 'http://test3.com')
