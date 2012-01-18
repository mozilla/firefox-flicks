from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from session_csrf import anonymous_csrf

from flicks.videos.models import Video

PAGINATION_LIMIT_MINI = 3
PAGINATION_LIMIT_FULL = 9


@anonymous_csrf
def home(request):
    """Landing page for Flicks. Displays all videos.
    If the total number of videos is less than 50, we
    want to only return 3 per request - otherwise, we
    want to return 9 per request.
    """
    show_pagination = False
    videos = Video.objects.all()

    if videos.count < 50:
        pagination_limit = PAGINATION_LIMIT_MINI
    else:
        pagination_limit = PAGINATION_LIMIT_FULL

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
             show_pagination=show_pagination)

    return render(request, 'home.html', d)


@anonymous_csrf
def creative(request):
    """Creative Brief page."""
    return render(request, 'creative.html')


@anonymous_csrf
def judges(request):
    """Judges page."""
    return render(request, 'judges.html')


@anonymous_csrf
def prizes(request):
    """Judges page."""
    return render(request, 'judges.html')


@anonymous_csrf
def partners(request):
    """Partners page."""
    return render(request, 'partners.html')


@anonymous_csrf
def faq(request):
    """FAQ page."""
    return render(request, 'faq.html')


@anonymous_csrf
def legal(request):
    """Legal page."""
    return render(request, 'legal.html')
