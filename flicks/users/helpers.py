import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.hashcompat import md5_constructor

from jingo import register
from jinja2 import Markup

from flicks.base.util import absolutify
from flicks.users.models import UserProfile


GRAVATAR_URL = getattr(settings, 'GRAVATAR_URL', 'https://secure.gravatar.com')
DEFAULT_GRAVATAR = absolutify(staticfiles_storage.url('img/avatar.png'))


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
    return Markup('<img class="%(class)s" src="%(src)s" '
        'width="%(width)s">' % {
        'class': img_class,
        'src': gravatar_url(arg, size=size),
        'width': size
    })


@register.function
def profile_name(user):
    try:
        return user.userprofile.full_name
    except UserProfile.DoesNotExist:
        return ''
