from nose.tools import ok_

from flicks.base.tests import TestCase
from flicks.users.management.commands import wipe_spectator_personal_info
from flicks.users.models import UserProfile
from flicks.users.tests import UserFactory, UserProfileFactory
from flicks.videos.tests import Video2013Factory


class WipeSpectatorPersonalInfoTests(TestCase):
    def test_command(self):
        """If a user has not uploaded any videos, their profile should be deleted."""
        user_with_profile_no_videos = UserProfileFactory.create().user
        user_no_profile_no_videos = UserFactory.create()
        user_with_profile_with_videos = UserProfileFactory.create().user
        user_no_profile_with_videos = UserFactory.create()  # Shouldn't exist, but we'll test.

        Video2013Factory.create(user=user_with_profile_with_videos)
        Video2013Factory.create(user=user_no_profile_with_videos)

        command = wipe_spectator_personal_info.Command()
        command.handle()

        ok_(not UserProfile.objects.filter(user=user_with_profile_no_videos).exists())
        ok_(not UserProfile.objects.filter(user=user_no_profile_no_videos).exists())
        ok_(UserProfile.objects.filter(user=user_with_profile_with_videos).exists())
        ok_(not UserProfile.objects.filter(user=user_no_profile_with_videos).exists())
