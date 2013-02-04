from django.conf import settings

from celery.decorators import task

from flicks.base.util import get_object_or_none
from flicks.videos import vimeo
from flicks.videos.models import Video


@task
def process_video(video_id):
    """Update metadata about the given video on Vimeo."""
    video = get_object_or_none(Video, id=video_id)
    if video:
        vimeo.setTitle(video.vimeo_id, video.title)

        # Set description to title + author + description.
        description = '{title} by {author}\n\n{description}'.format(
            title=video.title, author=video.user.profile.display_name,
            description=video.description)
        vimeo.setDescription(video.vimeo_id, description)

        # Add to the channel for the user's region.
        channels = settings.VIMEO_REGION_CHANNELS
        channel_id = channels.get(video.user.profile.region, None)
        if channel_id:
            vimeo.addToChannel(video.vimeo_id, channel_id)

        # Set their country code as a tag.
        vimeo.addTags(video.vimeo_id, [video.user.profile.country])

        video.processed = True
        video.save()
