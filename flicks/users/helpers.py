import urllib

from django.conf import settings
from django.utils.hashcompat import md5_constructor

from jingo import register
from jinja2 import Markup

from flicks.base.util import absolutify
from flicks.users.models import User


GRAVATAR_URL = getattr(settings, 'GRAVATAR_URL', 'http://www.gravatar.com')
DEFAULT_GRAVATAR = absolutify(settings.DEFAULT_GRAVATAR)


@register.function
def gravatar_url(arg, size=80):
    if isinstance(arg, User):
        email = arg.email
    else:  # Treat as email
        email = arg

    url = '%(url)s/avatar/%(email_hash)s?%(options)s' % {
        'url': GRAVATAR_URL,
        'email_hash': md5_constructor(email.lower()).hexdigest(),
        'options': urllib.urlencode({'s': str(size),
                                     'default': DEFAULT_GRAVATAR})
    }

    return url


@register.function
def gravatar_img(arg, size=80, img_class=None):
    return Markup('<img class="%(class)s" src="%(src)s">' % {
        'class': img_class,
        'src': gravatar_url(arg, size=size)
    })
