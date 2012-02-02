from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

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
    return render(request, 'creative.html')


def judges(request):
    """Judges page."""
    return render(request, 'judges.html')


def prizes(request):
    """Prizes page."""
    return render(request, 'prizes.html')


def partners(request):
    """Partners page."""
    return render(request, 'partners.html')


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html')


def rules(request):
    """Contest Rules page."""
    return render(request, 'rules.html')
