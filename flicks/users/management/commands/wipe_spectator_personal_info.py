from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Wipe personal info for users who have not submitted any videos.'

    def handle(self, *args, **kwargs):
        print 'Deleting spectator profiles...'
        for user in User.objects.all():
            if user.profile and self.is_spectator(user):
                print 'Deleting profile for {0}.'.format(user.profile.display_name)
                user.profile.delete()
        print 'Done.'

    def is_spectator(self, user):
        """Return True if the user has never uploaded a video to Flicks."""
        return user.video2013_set.count() < 1
