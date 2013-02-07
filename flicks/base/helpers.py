import json as json_mod

from django.utils.translation import get_language

from babel.core import Locale, UnknownLocaleError
from babel.dates import format_date
from jingo import register
from product_details import product_details

from flicks.base.util import absolutify as real_absolutify


def _babel_locale():
    """Return the current locale in Babel's format."""
    try:
        return Locale.parse(get_language(), sep='-')
    except UnknownLocaleError:
        # Default to en-US
        return Locale('en', 'US')


@register.filter
def babel_date(date, format='long'):
    """Format a date properly for the current locale. Format can be one of
    'short', 'medium', 'long', or 'full'.
    """
    locale = _babel_locale()
    return format_date(date, format, locale)


@register.filter
def json(data):
    return json_mod.dumps(data)


@register.function
def country_name(country_code):
    """Return a localized version of a country's name."""
    locale = get_language()

    # product_details has no `es` regional information, so we us es-ES instead.
    if locale == 'es':
        locale = 'es-ES'

    return product_details.get_regions(locale)[country_code]


@register.function
def absolutify(url):
    return real_absolutify(url)
