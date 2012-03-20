import json
import socket

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from jinja2 import Markup

import commonware.log
from django_statsd.clients import statsd
from tower import ugettext_lazy as _lazy

from flicks.base.util import get_object_or_none, promo_video_shortlink
from flicks.users.decorators import profile_required
from flicks.videos.forms import SearchForm, UploadForm
from flicks.videos.models import Video
from flicks.videos.tasks import send_video_to_vidly
from flicks.videos.util import (add_view, cached_viewcount,
                                send_video_complete_email,
                                send_video_error_email)
from flicks.videos.vidly import embedCode, parseNotify


TWEET_TEXT = _lazy("Check out '%(video_title)s' on Firefox Flicks. %(link)s")
log = commonware.log.getLogger('f.videos')


def recent(request):
    """List all videos, by recency."""
    show_pagination = False

    # Handle search and filtering
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        videos = search_form.videos()
    else:
        videos = Video.objects.filter(state='complete').order_by('-id')

    pagination_limit = getattr(settings, 'PAGINATION_LIMIT_FULL', 9)

    paginator = Paginator(videos, pagination_limit)
    page = request.GET.get('page', 1)

    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    if paginator.count > pagination_limit:
        show_pagination = True

    d = dict(search_form=search_form,
             search=False,
             videos=videos.object_list,
             video_pages=videos,
             show_pagination=show_pagination,
             page_type='secondary')

    return render(request, 'videos/recent.html', d)


def details(request, video_id=None):
    """Landing page for video details."""
    video = get_object_or_404(Video, pk=video_id, state='complete')

    # Check if admin is marking this video for judging.
    if request.POST.get('admin_mark', None) is not None:
        if request.user.is_staff:
            video.judge_mark = True
            video.save()

    viewcount = cached_viewcount(video_id)
    tweet_text = TWEET_TEXT % {'video_title': video.title[0:90],
                               'link': ''}  # URL is now included via JS

    d = dict(video=video,
             viewcount=viewcount,
             page_type='video-view',
             tweet_text=tweet_text)

    return render(request, 'videos/details.html', d)


@require_POST
def ajax_add_view(request):
    video_id = request.POST.get('video_id', None)
    if video_id is None:
        raise Http404

    try:
        viewcount = add_view(int(video_id))

        # Increment graphite stats
        statsd.incr('video_views')  # Total view count
        statsd.incr('video_views_%s' % video_id)
    except ValueError:
        raise Http404  # video_id is not an integer

    if viewcount is None:
        raise Http404

    return HttpResponse()


def promo_video_noir(request):
    """Film Noir promo video."""
    d = dict(video_title=_lazy('Noir'),
             video_description=_lazy('The fox meets a damsel in distress, but '
                                     'can he help her? Get inspired for your '
                                     'Firefox Flicks entry by checking out '
                                     'our video.'),
             page_type='videos',
             video_embed=Markup(embedCode(promo_video_shortlink('noir'),
                                          width=600, height=337)))
    return render(request, 'videos/promo.html', d)


def promo_video_dance(request):
    """Dancing promo video."""
    d = dict(video_title=_lazy('Dance'),
             video_description=_lazy("He's got the moves, he's got ambition. "
                                     "How far can this fox's feet take him? "
                                     "Get inspired for your Firefox Flicks "
                                     "entry by checking out our video."),
             page_type='videos',
             video_embed=Markup(embedCode(promo_video_shortlink('dance'),
                                          width=600, height=337)))
    return render(request, 'videos/promo.html', d)


def promo_video_twilight(request):
    """Twilight parody promo video."""
    d = dict(video_title=_lazy('Twilight'),
             video_description=_lazy('A teenage girl learns the truth about '
                                     'the fox. Get inspired for your Firefox '
                                     'Flicks entry by checking out our '
                                     'video.'),
             page_type='videos',
             video_embed=Markup(embedCode(promo_video_shortlink('twilight'),
                                          width=600, height=337)))
    return render(request, 'videos/promo.html', d)


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

            # Update statsd graph for uploads
            statsd.incr('video_uploads')

            return render(request, 'videos/upload_complete.html')
    else:
        form = UploadForm()

    d = dict(upload_form=form,
             page_type='secondary form')

    return render(request, 'videos/upload.html', d)


@require_POST
@csrf_exempt
def notify(request, key):
    """Process vid.ly notification requests."""
    # Verify key matches stored key.
    if key != settings.NOTIFY_KEY:
        return HttpResponseForbidden()

    notification = parseNotify(request)

    # Check for finished videos.
    for task in notification['tasks']:
        if task.finished:
            video = get_object_or_none(Video, shortlink=task.shortlink)
            if video is not None:
                video.state = 'complete'
                video.save()
                send_video_complete_email(video)

    # Check for video errors
    for error in notification['errors']:
        video = get_object_or_none(Video, shortlink=error.shortlink)
        if video is not None:
            video.state = 'error'
            video.save()
            send_video_error_email(video)

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
