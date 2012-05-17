import json
import socket

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from jinja2 import Markup

import commonware.log
import waffle
from django_statsd.clients import statsd
from tower import ugettext_lazy as _lazy

from flicks.base.util import get_object_or_none, promo_video_shortlink, redirect
from flicks.videos.forms import SearchForm
from flicks.videos.models import CATEGORY_CHOICES, Award, Video
from flicks.videos.util import add_view, cached_viewcount
from flicks.videos.vidly import embedCode


TWEET_TEXT = _lazy("Check out '%(video_title)s' on Firefox Flicks. %(link)s")
log = commonware.log.getLogger('f.videos')

WINNER_CATEGORIES = [c for c in CATEGORY_CHOICES if c[0] != 'new_technology']


def winners(request):
    """Winners page."""
    if not waffle.flag_is_active(request, 'winners_page'):
        return redirect('flicks.videos.recent')

    d = dict(
        awards={},
        category_choices=WINNER_CATEGORIES,
        page_type='winners'
    )

    # Add awards to template context
    grand_prize_awards = Award.objects.filter(award_type='grand_winner')
    for a in grand_prize_awards:
        key = '{0}__{1}'.format(a.award_type, a.region)
        d['awards'][key] = a

    awards = Award.objects.filter(award_type__in=['category_winner',
                                                  'runner_up'])
    for a in awards:
        key = '{0}__{1}__{2}'.format(a.award_type, a.region, a.category)
        d['awards'][key] = a

    d['awards']['panavision'] = Award.objects.filter(award_type='panavision')
    d['awards']['bavc'] = Award.objects.get(award_type='bavc')

    return render(request, 'videos/winners.html', d)


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
             show_pagination=show_pagination)

    if waffle.flag_is_active(request, 'winners_page'):
        template = 'videos/recent.html'
        d['page_type'] = 'secondary recent'
    else:
        template = 'videos/recent_contest_over.html'
        d['page_type'] = 'secondary recent closed'

    return render(request, template, d)


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
             tweet_text=_lazy('The fox meets a damsel in distress, but can he '
                              'help her?'),
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
             tweet_text=_lazy("He's got the moves. He's got ambition. How far "
                              "can this fox's feet take him?"),
             page_type='videos',
             video_embed=Markup(embedCode(promo_video_shortlink('dance'),
                                          width=600, height=337)))
    return render(request, 'videos/promo.html', d)


def promo_video_twilight(request):
    """Twilight parody promo video."""
    desc = _lazy('A teenage girl learns the truth about the fox. Get inspired '
                 'for your Firefox Flicks entry by checking out our video.')
    d = dict(video_title=_lazy('Twilight'),
             video_description=desc,
             tweet_text=desc,
             page_type='videos',
             video_embed=Markup(embedCode(promo_video_shortlink('twilight'),
                                          width=600, height=337)))
    return render(request, 'videos/promo.html', d)


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
