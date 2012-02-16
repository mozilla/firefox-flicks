from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

import commonware.log
import requests
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


def get_object_or_none(model_class, **filters):
    """Identical to Model.get, except instead of throwing exceptions, this
    returns None.
    """
    try:
        return model_class.objects.get(**filters)
    except (model_class.DoesNotExist, model_class.MultipleObjectsReturned):
        return None


def generate_bitly_link(url):
    """Generates a mzl.la shortlink."""
    try:
        response = requests.get(settings.BITLY_API_SHORTEN, params={
            'login': settings.BITLY_API_LOGIN,
            'apiKey': settings.BITLY_API_KEY,
            'format': 'txt',
            'longUrl': url
        })
    except requests.exceptions.RequestException, e:
        # If there was an issue, return None
        log.error('Error generating Bit.ly shortlink: %s' % e)
        return None

    # If we don't get a 200, return None
    if response.status_code != 200:
        log.error('Error generating Bit.ly shortlink: %s %s' %
                  (response.status_code, response.content))
        return None

    return response.content.strip()
