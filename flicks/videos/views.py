import socket

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import commonware.log

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
