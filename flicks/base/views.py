from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import render

from flicks.base.util import absolutify
from flicks.videos.models import Video


def home(request):
    """Landing page for Flicks. Displays all videos.
    If the total number of videos is less than 50, we
    want to only return 3 per request - otherwise, we
    want to return 9 per request.
    """
    show_pagination = False
    videos = Video.objects.filter(state='complete').order_by('-id')

    if videos.count < 50:
        pagination_limit = getattr(settings, 'PAGINATION_LIMIT_MINI', 3)
    else:
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

    d = dict(videos=videos.object_list,
             show_pagination=show_pagination,
             page_type='home')

    return render(request, 'home.html', d)


def creative(request):
    """Creative Brief page."""
    d = dict(
        promo_dance=absolutify(reverse('flicks.videos.promo_video_dance')),
        promo_noir=absolutify(reverse('flicks.videos.promo_video_noir')),
        promo_twilight=absolutify(
            reverse('flicks.videos.promo_video_twilight')),
        page_type='secondary'
    )

    return render(request, 'creative.html', d)


def judges(request):
    """Judges page."""
    return render(request, 'judges.html', {'page_type': 'secondary'})


def prizes(request):
    """Prizes page."""
    return render(request, 'prizes.html', {'page_type': 'secondary'})


def partners(request):
    """Partners page."""
    return render(request, 'partners.html', {'page_type': 'secondary'})


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html')


def rules(request):
    """Contest Rules page."""
    return render(request, 'rules.html')
