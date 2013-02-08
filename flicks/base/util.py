from contextlib import contextmanager
from locale import strcoll as locale_strcoll

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.functional import lazy
from django.utils.translation import get_language

import commonware.log
from funfactory.urlresolvers import reverse
from tower import activate


log = commonware.log.getLogger('f.base')


def absolutify(url):
    """Add domain and protocol to link."""
    glue = '' if url.startswith('/') else '/'
    return glue.join((settings.SITE_URL, url))


def redirect(to, permanent=False, anchor=None, **kwargs):
    """
    Returns a redirect response by applying funfactory's locale-aware reverse
    to the given string.

    Pass in permanent=True to return a permanent redirect. All other keyword
    arguments are passed to reverse.
    """
    if permanent:
        redirect_class = HttpResponsePermanentRedirect
    else:
        redirect_class = HttpResponseRedirect

    url = reverse(to, **kwargs)
    if anchor:
        url = '#'.join([url, anchor])

    return redirect_class(url)


def _reverse_lazy(*args, **kwargs):
    # We have to force this to be a string because Django's urlparse function
    # chokes on __proxy__ objects that don't resolve to a str and funfactory
    # returns unicode. See https://github.com/mozilla/funfactory/pull/47 for
    # details.
    return str(reverse(*args, **kwargs))
reverse_lazy = lazy(_reverse_lazy, str)


def get_object_or_none(model_class, **filters):
    """Identical to Model.get, except instead of throwing exceptions, this
    returns None.
    """
    try:
        return model_class.objects.get(**filters)
    except (model_class.DoesNotExist, model_class.MultipleObjectsReturned):
        return None


def promo_video_shortlink(promo_name):
    """Returns a promo video for the current locale, defaulting to en-US if
    none is found.
    """
    videos = settings.PROMO_VIDEOS.get(promo_name, None)
    if videos is None:
        return None

    lang = get_language()
    video = videos.get(lang, None)
    if video is None:
        video = videos.get('en-us', None)

    return video


def unicode_choice_sorted(choices):
    """
    Sorts a list of 2-tuples by the second value, using a unicode-safe sort.
    """
    return sorted(choices, cmp=lambda x, y: locale_strcoll(x[1], y[1]))


def country_choices(allow_empty=True):
    """Return a localized, sorted list of tuples of country names and values."""
    from product_details import product_details

    regions = product_details.get_regions(get_language())

    # Filter out ineligible countries.
    for country in settings.INELIGIBLE_COUNTRIES:
        if country in regions:
            del regions[country]

    items = regions.items()
    if allow_empty:
        items.append(('', '---'))

    return unicode_choice_sorted(items)


@contextmanager
def use_lang(lang):
    """Temporarily use another language for translation."""
    current_lang = get_language()
    activate(lang)
    yield
    activate(current_lang)
