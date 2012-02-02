import json
import socket

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import commonware.log

from flicks.base.util import get_object_or_none
from flicks.users.decorators import profile_required
from flicks.videos.forms import UploadForm
from flicks.videos.models import Video
from flicks.videos.tasks import send_video_to_vidly
from flicks.videos.vidly import parseNotify


log = commonware.log.getLogger('f.videos')


def details(request, video_id=None):
    """Landing page for video details."""
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'videos/details.html', {'video': video})


@profile_required
def upload(request):
    """Video upload page."""
    if request.method == 'POST':
        form = UploadForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()

            # Celery times out sometimes; we'll catch orphaned
            # videos with a cron job.
            try:
                send_video_to_vidly.delay(video)
            except socket.timeout:
                log.warning('Timeout connecting to celery to convert video '
                            'id: %s' % video.id)

            return render(request, 'videos/upload_complete.html')
    else:
        form = UploadForm()

    return render(request, 'videos/upload.html', {'upload_form': form})


@require_POST
@csrf_exempt
def notify(request):
    """Process vid.ly notification requests."""
    notification = parseNotify(request)

    # Verify that user id matches to avoid spoofing (kind've weak)
    if notification and notification['user_id'] == settings.VIDLY_USER_ID:
        try:
            video = Video.objects.get(shortlink=notification['shortlink'])
            video.state = 'complete'
            video.save()
        except Video.DoesNotExist:
            log.warning('Vid.ly notification with shortlink that does not '
                        'exist: %s' % notification['shortlink'])

    return HttpResponse()


@require_POST
def upvote(request, video_shortlink):
    """Add an upvote to a video."""
    response = HttpResponse(mimetype='application/json')
    if video_shortlink in request.COOKIES:
        response.status_code = 403
        response.content = json.dumps({'error': 'already voted'})
        return response

    video = get_object_or_none(Video, shortlink=video_shortlink)
    if video is not None:
        try:
            video.upvote()
        except socket.timeout:
            log.warning('Timeout connecting to celery to upvote video '
                        'shortlink: %s' % video_shortlink)
            response.status_code = 500
            response.content = json.dumps({'error': 'celery timeout'})
        else:
            response.set_cookie(str(video_shortlink), value='1',
                                httponly=False,
                                max_age=settings.VOTE_COOKIE_AGE)
            response.content = json.dumps({'success': 'success'})
    else:
        response.status_code = 404
        response.content = json.dumps({'error': 'video not found'})


    return response
