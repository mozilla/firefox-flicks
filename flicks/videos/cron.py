import commonware.log
import cronjobs

from django.core.cache import cache

from celery.task.sets import TaskSet
from celeryutils import chunked

from flicks.videos.models import Video
from flicks.videos.util import VIEWS_KEY

log = commonware.log.getLogger('m.cron')


@cronjobs.register
def reindex_videos():
    from elasticutils import tasks

    ids = (Video.objects.values_list('id', flat=True))

    ts = [tasks.index_objects.subtask(args=[Video, chunk]) for
          chunk in chunked(sorted(list(ids)), 150)]
    TaskSet(ts).apply_async()


@cronjobs.register
def persist_viewcounts():
    """Check the cache for stored view counts and write them to the DB."""
    ids = (Video.objects.values_list('id', flat=True))
    for video_id in ids:
        viewcount = cache.get(VIEWS_KEY % video_id)
        if viewcount is not None:
            Video.objects.filter(id=video_id).update(views=viewcount)
