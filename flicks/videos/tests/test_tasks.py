from mock import patch
from nose.tools import ok_

from flicks.base import regions
from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos.tasks import process_video
from flicks.videos.tests import VideoFactory


@patch('flicks.videos.tasks.vimeo')
class TestProcessVideo(TestCase):
    def test_no_video(self, vimeo):
        """If no video is found with the given id, do nothing."""
        process_video(1387589156831)
        ok_(not vimeo.setTitle.called)
        ok_(not vimeo.setDescription.called)
        ok_(not vimeo.addToChannel.called)
        ok_(not vimeo.addTags.called)

    def test_valid_video(self, vimeo):
        """If a valid video id is given, update the Vimeo metadata."""
        user = UserProfileFactory.create(nickname='name', country='us').user
        video = VideoFactory.create(user=user, title='blah', description='asdf',
                                    vimeo_id=7)

        with self.settings(VIMEO_REGION_CHANNELS={regions.NORTH_AMERICA: 18}):
            process_video(video.id)

        vimeo.setTitle.assert_called_with(7, 'blah')
        vimeo.setDescription.assert_called_with(7, 'blah by name\n\nasdf')
        vimeo.addToChannel.assert_called_with(7, 18)
        vimeo.addTags.assert_called_with(7, ['us'])
