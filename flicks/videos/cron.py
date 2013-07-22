import cronjobs

from flicks.videos.models import Video


@cronjobs.register
def update_random_video_ordering():
    print 'Updating random video ordering...'
    for index, video in enumerate(Video.objects.order_by('?')):
        video.random_ordering = index
        video.save()
    print 'Done!'
