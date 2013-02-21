from django.contrib.auth.models import Permission

from mock import ANY, patch
from nose.tools import ok_

from flicks.base import regions
from flicks.base.tests import TestCase
from flicks.base.tests.tools import CONTAINS
from flicks.users.tests import GroupFactory, UserFactory, UserProfileFactory

from flicks.videos.tasks import process_video
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
