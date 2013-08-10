import operator

from django.db.models import Count, Q

from flicks.base import regions
from flicks.videos.models import Video


AUTOCOMPLETE_FIELDS = {
    'title': ('title',),
    'description': ('description',),
    'author': ('user__userprofile__full_name', 'user__userprofile__nickname')
}

DEFAULT_QUERY_FIELDS = ('title', 'description', 'user__userprofile__full_name',
                        'user__userprofile__nickname')


def search_videos(query='', fields=None, region=None, sort=None):
    """
    Retrieve a sorted list of videos, optionally filtered by a text search
    query and region.

    :param query:
        Search query. The video title and description are searched, as well as
        the full name of the user who created the video. Limited to a simple
        "icontains" filter.

    :param fields:
        Fields to apply search query to. Defaults to video title, description,
        and user's full name and nickname.

    :param region:
        If present, filters videos to only those found in the specified region.
        Values for this parameter can be found in `flicks.base.regions`.

    :param sort:
        How to sort the resulting videos. Defaults to a random sort that
        changes every hour. Other valid options are 'popular', which sorts by
        vote count, and 'title', which sorts alphabetically by title.
    """
    qs = Video.objects.filter(approved=True)
    query = query.strip()

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


def autocomplete_suggestion(query, fields):
    """
    Perform a search on a field or set of fields and return the value of those
    fields on the first result as a suggested autocompletion value.

    :param query:
        Search query that we are attempting to autocomplete.

    :param fields:
        Fields that we are attempting autocompletion for. Suggestions are
        prioritized based on the order of fields; if a match is found for the
        first field, it will be returned, otherwise the next field will be
        searched until a suggestion is found or all fields are searched.

    :returns: The value of the matched field on the matched Video, or None
    """
    for field in fields:
        try:
            result = search_videos(query=query, fields=(field,))
            return result.values(field)[0][field]
        except (AttributeError, IndexError):
            pass

    return None
