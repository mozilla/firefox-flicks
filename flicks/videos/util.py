from django.core.cache import cache

from flicks.base.util import get_object_or_none
from flicks.videos.models import Video


VIEWS_KEY = 'VIEWCOUNT_%s'


def add_view(video_id):
    """Add a view to the view count for the video.

    Views are stored in the cache and are periodically stored back to the
    database. How often this happens depends on the view count.
    """
    # Ensure that the view count is in the cache.
    viewcount = cached_viewcount(video_id)
    if viewcount is None:
        return None

    key = VIEWS_KEY % video_id
    viewcount = cache.incr(key)
    save_viewcount = (
        (viewcount < 10) or
        (viewcount < 100 and viewcount % 5 == 0) or
        (viewcount < 1000 and viewcount % 50 == 0) or
        (viewcount > 1000 and viewcount % 100 == 0)
    )

    if save_viewcount:
        Video.objects.filter(id=video_id).update(views=viewcount)

    return viewcount

def cached_viewcount(video_id):
    """Get the viewcount for the specified video from the cache. If the
    viewcount isn't in the cache, load it from the DB and store it in the
    cache.
    """
    key = VIEWS_KEY % video_id
    viewcount = cache.get(key)
    if viewcount is None:
        video = get_object_or_none(Video, id=video_id)
        if video is None:
            return None

        cache.set(key, video.views, 0)  # Cache indefinitely
        viewcount = video.views

    return viewcount
