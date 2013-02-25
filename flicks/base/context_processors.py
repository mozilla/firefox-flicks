from funfactory.helpers import static
from funfactory.urlresolvers import reverse
from tower import ugettext as _


def browserid_request_args(request):
    request_args = {
        'privacyPolicy': 'http://www.mozilla.org/en-US/privacy-policy.html',
        'siteName': _('Firefox Flicks'),
        'termsOfService': reverse('flicks.base.rules'),
    }

    if request.is_secure():
        request_args['siteLogo'] = static('img/flicks-logo-180.png')

    return {'browserid_request_args': request_args}
