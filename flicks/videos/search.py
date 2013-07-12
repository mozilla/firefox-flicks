import operator

from django.db.models import Count, Q

from flicks.base import regions
from flicks.videos.models import Video


def search_videos(query=None, region=None, sort=None):
    """
    Retrieve a sorted list of videos, optionally filtered by a text search
    query and region.

    :param query:
        Search query. The video title and description are searched, as well as
        the full name of the user who created the video. Limited to a simple
        "icontains" filter.

    :param region:
        If present, filters videos to only those found in the specified region.
        Values for this parameter can be found in `flicks.base.regions`.

    :param sort:
        How to sort the resulting videos. Defaults to alphabetical by title
        sort. Only other valid option is 'popular' which sorts by vote count.
    """
    qs = Video.objects.filter(approved=True)

    # Text search
    if query:
        filters = []
        for term in query.split(None, 6):  # Limit to 6 to guard against abuse.
            filters.extend([
                Q(title__icontains=term),
                Q(description__icontains=term),
                Q(user__userprofile__full_name__icontains=term)
            ])
        qs = qs.filter(reduce(operator.or_, filters))  # Mash 'em all together!

    # Filter by region
    if region:
        countries = regions.get_countries(region)
        if countries:
            qs = qs.filter(user__userprofile__country__in=countries)

    # Sorting
    if sort == 'popular':
        qs = qs.annotate(vote_count=Count('voters')).order_by('-vote_count')
    else:
        qs = qs.order_by('title')  # Default sort is by title.

    return qs
