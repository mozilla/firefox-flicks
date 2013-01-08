from contextlib import contextmanager

from django.conf import settings

from elasticutils import get_es


from flicks.videos.models import Video


@contextmanager
def build_video(user, **kwargs):
    """Create a new video object, with default acceptable values. The video
    is deleted once the block is exited."""
    args = {'title': 'Test',
            'description': 'Test description',
            'user': user,
            'category': 'test',
            'region': 'test',
            'upload_url': 'http://test.com',
            'shortlink': 'test_shortlink',
            'state': 'complete',
            'votes': 0}
    args.update(kwargs)

    video = Video.objects.create(**args)

    # Refresh ES if possible.
    if not settings.ES_DISABLED:
        get_es().refresh(settings.ES_INDEXES['default'], timesleep=0)

    yield video
    video.delete()
