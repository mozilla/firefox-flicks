from django.db import models

from celery.decorators import task
from funfactory.urlresolvers import reverse

from flicks.base.util import absolutify
from flicks.videos.vidly import addMedia


@task
def send_video_to_vidly(video):
    """Send a video to vid.ly for processing."""
    shortlink = addMedia(video.upload_url,
                         absolutify(reverse('flicks.videos.notify')))

    if shortlink is None:
        video.state = 'error'
        video.save()
    else:
        video.shortlink = shortlink
        video.state = 'pending'
        video.save()


@task
def add_vote(video):
    """Add a vote to a video."""
    video.votes = models.F('votes') + 1
    video.save()
