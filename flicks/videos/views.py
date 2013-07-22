from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST

import waffle
from tower import ugettext as _
from waffle.decorators import waffle_flag

from flicks.base import regions
from flicks.base.http import JSONResponse
from flicks.base.util import promo_video_shortlink, redirect
from flicks.videos import tasks, vimeo
from flicks.videos.decorators import upload_process
from flicks.videos.forms import VideoForm, VideoSearchForm
from flicks.videos.models import Video, Video2012, Vote
from flicks.videos.search import autocomplete_suggestion, search_videos
from flicks.videos.util import vidly_embed_code
from flicks.users.decorators import profile_required


### 2013 Contest ###
# Video pages
def gallery(request):
    """Show the gallery of all submitted videos."""
    region = request.GET.get('region', None)
    ctx = {}

    if waffle.flag_is_active(request, 'r3'):
        form = VideoSearchForm(request.GET)
        try:
            videos = form.perform_search()
        except ValidationError:
            videos = search_videos()

        ctx['form'] = form
    else:
        videos = Video.objects.filter(approved=True).order_by('-created')
        if region:
            countries = regions.get_countries(region)
            if countries:
                videos = videos.filter(
                    user__userprofile__country__in=countries)

    return video_list(request, videos, ctx)


@waffle_flag('r3')
@login_required
def my_voted_videos(request):
    """Show videos that the current user has voted for."""
    # Order by most-recently voted.
    videos = request.user.voted_videos.order_by('-vote__id')
    return video_list(request, videos, {'hide_gallery_header': True})


def video_list(request, videos, ctx=None):
    """Show a list of videos."""
    page = request.GET.get('page', 1)
    ctx = ctx or {}

    if 'form' not in ctx:
        ctx['form'] = VideoSearchForm(request.GET)

    paginator = Paginator(videos, 12)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)  # Default to first page
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)  # Empty page goes to last

    ctx['videos'] = videos
    return render(request, 'videos/2013/list.html', ctx)


@waffle_flag('r3')
@cache_control(public=True, max_age=60*60*24*30)  # 30 days
def autocomplete(request):
    """Return results for the autocomplete feature on the search page."""
    query = request.GET.get('query', None)
    if not query:
        return HttpResponseBadRequest()

    results = {
        'by_title': autocomplete_suggestion(query, 'title'),
        'by_description': autocomplete_suggestion(query, 'description'),
        'by_author': autocomplete_suggestion(query,
                                             'user__userprofile__full_name'),
    }
    return JSONResponse(results)


def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'videos/2013/details.html', {'video': video})


def winners(request):
    return render(request, 'videos/2013/winners.html', {'datetime': datetime})


# Voting
@waffle_flag('r3')
@require_POST
def vote(request, video_id):
    """
    Attempt to vote for a video. If the user isn't authenticated, store their
    intent in the session. Once they login the vote will register.
    """
    if request.user.is_authenticated():
        video = get_object_or_404(Video, id=video_id)
        Vote.objects.get_or_create(user=request.user, video=video)
    else:
        request.session['vote_video'] = video_id
    return HttpResponse()


@waffle_flag('r3')
@require_POST
def unvote(request, video_id):
    if not request.user.is_authenticated():
        return HttpResponseNotFound()
    else:
        vote = get_object_or_404(Vote, user=request.user, video__id=video_id)
        vote.delete()
        return HttpResponse()


# Upload process
@profile_required
@upload_process
def upload(request):
    ticket = request.session.get('vimeo_ticket', None)
    form = VideoForm(request.POST or None)
    if ticket and request.method == 'POST' and form.is_valid():
        # Verify that the filesize from the client matches what vimeo received.
        # Some browsers don't provide this number, so we can't really verify.
        filesize = form.cleaned_data['filesize']
        if filesize and not vimeo.verify_chunks(ticket['id'], filesize):
            return upload_error(request)

        ticket = vimeo.complete_upload(ticket['id'],
                                       form.cleaned_data['filename'])

        # Create video and schedule it for processing.
        video = form.save(commit=False)
        video.user = request.user
        video.vimeo_id = ticket['video_id']
        video.save()
        tasks.process_video.delay(video.id)

        del request.session['vimeo_ticket']
        return redirect('flicks.videos.upload_complete')

    # Generate an upload token if one doesn't exist or isn't valid.
    if not ticket or not vimeo.is_ticket_valid(ticket['id']):
        ticket = vimeo.get_new_ticket()
        request.session['vimeo_ticket'] = ticket

    return render(request, 'videos/upload.html', {
        'ticket': ticket,
        'form': form
    })


@upload_process
def upload_complete(request):
    return render(request, 'videos/upload_complete.html')


@upload_process
def upload_error(request):
    return render(request, 'videos/upload_error.html', status=500)


### 2012 Archive ###
def details_2012(request, video_id=None):
    """Landing page for video details."""
    video = get_object_or_404(Video2012, pk=video_id, state='complete')
    return render(request, 'videos/2012/details.html', {'video': video})


def promo_video_noir(request):
    """Film Noir promo video."""
    d = dict(video_title=_('Noir'),
             video_description=_('The fox meets a damsel in distress, but can '
                                 'he help her? Get inspired for your Firefox '
                                 'Flicks entry by checking out our video.'),
             tweet_text=_('The fox meets a damsel in distress, but can he help '
                          'her?'),
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('noir'),
                                          width='100%'))
    return render(request, 'videos/2012/promo.html', d)


def promo_video_dance(request):
    """Dancing promo video."""
    d = dict(video_title=_('Dance'),
             video_description=_("He's got the moves, he's got ambition. How "
                                 "far can this fox's feet take him? Get "
                                 "inspired for your Firefox Flicks entry by "
                                 "checking out our video."),
             tweet_text=_("He's got the moves. He's got ambition. How far can "
                          "this fox's feet take him?"),
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('dance'),
                                          width='100%'))
    return render(request, 'videos/2012/promo.html', d)


def promo_video_twilight(request):
    """Twilight parody promo video."""
    desc = _('A teenage girl learns the truth about the fox. Get inspired for '
             'your Firefox Flicks entry by checking out our video.')
    d = dict(video_title=_('Twilight'),
             video_description=desc,
             tweet_text=desc,
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('twilight'),
                                          width='100%'))
    return render(request, 'videos/2012/promo.html', d)
