from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string

from flicks.base.util import get_object_or_none
from flicks.videos.decorators import vimeo_task
from flicks.videos.util import send_approval_email, send_rejection_email


# We explicitly import flicks.videos.vimeo here in order to register the Vimeo
# API methods as tasks.
from flicks.videos import vimeo


@vimeo_task
def process_video(video_id):
    """Update metadata about the given video on Vimeo."""
    from flicks.videos.models import Video

    video = get_object_or_none(Video, id=video_id)
    if video:
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


@vimeo_task
def process_approval(video_id):
    """Update privacy and gather more metadata once a video is approved."""
    from flicks.videos.models import Video

    video = get_object_or_none(Video, id=video_id)
    if video:
        if video.approved:
            vimeo.set_privacy(video.vimeo_id, 'anybody')

            # Send an email out if the user hasn't been notified.
            if not video.user_notified:
                send_approval_email(video)
                video.user_notified = True

            # Pull the thumbnail url for the video. We pull it here instead of
            # during processing to give Vimeo a chance to finish encoding and
            # processing the video on their side.
            thumbnails = vimeo.get_thumbnail_urls(video.vimeo_id)
            for thumbnail in thumbnails:
                if thumbnail['height'] == '75':
                    video.small_thumbnail_url = thumbnail['_content']
                elif thumbnail['height'] == '150':
                    video.medium_thumbnail_url = thumbnail['_content']
                elif thumbnail['height'] == '480':
                    video.large_thumbnail_url = thumbnail['_content']

            video.save()
        else:
            vimeo.set_privacy(video.vimeo_id, 'password',
                              password=settings.VIMEO_VIDEO_PASSWORD)


@vimeo_task
def process_deletion(vimeo_id, user_id):
    vimeo.delete_video(vimeo_id)
    send_rejection_email(user_id)
