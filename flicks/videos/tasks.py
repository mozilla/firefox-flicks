from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string

from celery.decorators import task

from flicks.base.util import get_object_or_none
from flicks.videos import vimeo
from flicks.videos.models import Video


@task(default_retry_delay=30 * 60)  # Retry once every 30 minutes.
def process_video(video_id):
    """Update metadata about the given video on Vimeo."""
    video = get_object_or_none(Video, id=video_id)
    if video:
        try:
            vimeo.set_title(video.vimeo_id, video.title)

            # Set description to title + author + description.
            description = '{title} by {author}\n\n{description}'.format(
                title=video.title, author=video.user.profile.display_name,
                description=video.description)
            vimeo.set_description(video.vimeo_id, description)

            # Add to the channel for the user's region.
            channels = settings.VIMEO_REGION_CHANNELS
            channel_id = channels.get(video.user.profile.region, None)
            if channel_id:
                vimeo.add_to_channel(video.vimeo_id, channel_id)

            # Set their country code as a tag.
            vimeo.add_tags(video.vimeo_id, [video.user.profile.country])

            video.processed = True
            video.save()
        except vimeo.VimeoServiceError, e:
            # If Vimeo is down, retry later.
            raise process_video.retry(exc=e)

        # Email moderators that a video has finished processing and is ready
        # for review.
        perm = Permission.objects.get(codename='change_video2013')
        moderators = User.objects.filter(Q(groups__permissions=perm) |
                                         Q(user_permissions=perm)).distinct()

        subject = ('[flicks-moderation] `{0}` is ready for review'
                   .format(video.title))
        message = render_to_string('videos/2013/moderation_email.html',
                                   {'video': video})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [u.email for u in moderators])
