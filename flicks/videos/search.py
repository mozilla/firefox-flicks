import operator

from django.db.models import Count, Q

from flicks.base import regions
from flicks.videos.models import Video


DEFAULT_QUERY_FIELDS = ('title', 'description', 'user__userprofile__full_name')


def search_videos(query=None, fields=None, region=None, sort=None):
    """
    Retrieve a sorted list of videos, optionally filtered by a text search
    query and region.

    :param query:
        Search query. The video title and description are searched, as well as
        the full name of the user who created the video. Limited to a simple
        "icontains" filter.

    :param fields:
        Fields to apply search query to. Defaults to video title, description,
        and user's full name.

    :param region:
        If present, filters videos to only those found in the specified region.
        Values for this parameter can be found in `flicks.base.regions`.

    :param sort:
        How to sort the resulting videos. Defaults to a random sort that
        changes every hour. Other valid options are 'popular', which sorts by
        vote count, and 'title', which sorts alphabetically by title.
    """
    qs = Video.objects.filter(approved=True)

    # Text search
    if query:
        filters = []
        fields = fields or DEFAULT_QUERY_FIELDS
        for term in query.split(None, 6):  # Limit to 6 to guard against abuse.
            for field in fields:
                kwarg = '{0}__icontains'.format(field)
                filters.append(Q(**{kwarg: term}))
        qs = qs.filter(reduce(operator.or_, filters))  # Mash 'em all together!

    # Filter by region
    if region is not None:
        countries = regions.get_countries(region)
        if countries:
            qs = qs.filter(user__userprofile__country__in=countries)

    # Sorting
    if sort == 'popular':
        # NOTE: Naming this count `vote_count` triggers a bug in Django since
        # there's a property named that on the model.
        qs = qs.annotate(votecount=Count('voters')).order_by('-votecount')
    elif sort == 'title':
        qs = qs.order_by('title')  # Default sort is by title.
    else:
        qs = qs.order_by('random_ordering')

    return qs


def autocomplete_suggestion(query, field):
    """
    Perform a search on a specific field and return the value of that field on
    the first result as a suggested autocompletion value.

    :param query:
        Search query that we are attempting to autocomplete.

    :param field:
        Field that we are attempting autocompletion for.
    """
    try:
        result = search_videos(query=query, fields=(field,)).values(field)[0]
        return result[field]
    except IndexError:
        return None
