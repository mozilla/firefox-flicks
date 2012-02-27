import commonware.log
import cronjobs

from flicks.videos.models import Video
from celery.task.sets import TaskSet
from celeryutils import chunked

log = commonware.log.getLogger('m.cron')


@cronjobs.register
def reindex_videos():
    from elasticutils import tasks

    ids = (Video.objects.values_list('id', flat=True))

    ts = [tasks.index_objects.subtask(args=[Video, chunk]) for 
          chunk in chunked(sorted(list(ids)), 150)]
    TaskSet(ts).apply_async()
