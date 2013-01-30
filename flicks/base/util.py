from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.functional import lazy
from django.utils.translation import get_language

import commonware.log
from funfactory.urlresolvers import reverse


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
