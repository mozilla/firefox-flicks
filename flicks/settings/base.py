# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py
from funfactory.settings_base import *

from flicks.base import regions
from flicks.base.util import reverse_lazy

# Import locale-sensitive settings
from .locale import *

PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr', 'it', 'ja', 'lij', 'nl', 'pl',
                  'pt-BR', 'ru', 'sl', 'sq', 'zh-CN', 'zh-TW')

# Defines the views served for root URLs.
ROOT_URLCONF = 'flicks.urls'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Paths that do not need a locale
SUPPORTED_NONLOCALES += ['admin', 'robots.txt']

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'flicks.base',
    'flicks.users',
    'flicks.videos',

    'django.contrib.admin',

    'django_browserid',
    'django_statsd',
    'jingo_minify',
    'south',
    'waffle',
]

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + [
    'commonware.response.middleware.StrictTransportMiddleware',
    'csp.middleware.CSPMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'waffle.middleware.WaffleMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'django_browserid.context_processors.browserid',
]

# Authentication settings
LOGIN_URL = reverse_lazy('flicks.base.home')
LOGIN_REDIRECT_URL = reverse_lazy('flicks.base.home')
LOGIN_REDIRECT_URL_FAILURE = reverse_lazy('flicks.base.home')
LOGOUT_REDIRECT_URL = reverse_lazy('flicks.base.home')


# Lazy-load request args since they depend on certain settings.
def _request_args():
    from django.conf import settings

    from funfactory.helpers import static
    from tower import ugettext_lazy as _lazy

    args = {
        'privacyPolicy': 'http://www.mozilla.org/en-US/privacy-policy.html',
        'siteName': _lazy('Firefox Flicks'),
        'termsOfService': reverse_lazy('flicks.base.rules'),
    }

    if settings.SITE_URL.startswith('https'):
        args['siteLogo'] = static('img/flicks-logo-180.png')

    return args
BROWSERID_REQUEST_ARGS = lazy(_request_args, dict)()

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'browserid',
    'registration',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('**/flicks/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/flicks/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('**/flicks/**/templates/**.ltxt',
            'tower.management.commands.extract.extract_tower_template'),
    ],
}

# Always generate a CSRF token for anonymous users
ANON_ALWAYS = True

# Email Settings
DEFAULT_FROM_EMAIL = 'firefoxflicks@mozilla.com'

# Secure Cookies
SESSION_COOKIE_SECURE = True

# Set ALLOWED_HOSTS based on SITE_URL.
def _allowed_hosts():
    from django.conf import settings
    from urlparse import urlparse

    host = urlparse(settings.SITE_URL).netloc  # Remove protocol and path
    host = host.rsplit(':', 1)[0]  # Remove port
    return [host]
ALLOWED_HOSTS = lazy(_allowed_hosts, list)()

# Django-CSP
CSP_IMG_SRC = ("'self'",
               'data:',
               'https://*.gravatar.com',
               'https://*.google-analytics.com',
               'https://*.mozilla.org',
               'https://*.mozilla.net',)
CSP_STYLE_SRC = ("'self'",
                 "'unsafe-inline'",
                 'https://*.mozilla.org',
                 'https://*.mozilla.net',
                 'https://*.vimeo.com',)
CSP_FONT_SRC = ("'self'",
                'https://*.mozilla.org',
                'https://*.mozilla.net',)
CSP_SCRIPT_SRC = ("'self'",
                  'https://login.persona.org',
                  'https://*.google-analytics.com',
                  'https://*.mozilla.org',
                  'https://*.mozilla.net',)
CSP_FRAME_SRC = ("'self'",
                 'https://vid.ly',
                 'https://*.vimeo.com',
                 'https://*.vimeocdn.com',
                 'https://login.persona.org',)
CSP_DEFAULT_SRC = ("'self'",
                   'https://*.vimeo.com',)

# Activate statsd patches to time database and cache hits.
STATSD_PATCHES = [
    'django_statsd.patches.db',
    'django_statsd.patches.cache',
]

# Video preview settings
PREVIEW_PATH = lambda inst, filename: 'previews/images/%s_%s' % (inst.id, filename)
MAX_FILEPATH_LENGTH = 100

# Google Analytics
GA_ACCOUNT_CODE = ''

# Allow robots to crawl the site.
ENGAGE_ROBOTS = True

# Vimeo API
VIMEO_USER_ID = ''
VIMEO_CLIENT_KEY = u''
VIMEO_CLIENT_SECRET = u''
VIMEO_RESOURCE_OWNER_KEY = u''
VIMEO_RESOURCE_OWNER_SECRET = u''
VIMEO_VIDEO_PASSWORD = ''
VIMEO_REGION_CHANNELS = {
    regions.NORTH_AMERICA: None,
    regions.LATIN_AMERICA: None,
    regions.EMEA: None,
    regions.APAC: None,
}

# Countries that aren't eligible for Flicks
INELIGIBLE_COUNTRIES = ('cu', 'ir', 'kp', 'sd', 'sy')

# Basket (mailing list signups)
BASKET_URL = 'https://basket.mozilla.com'
BASKET_FLICKS_LIST = 'firefox-flicks'


# jingo-minify
JINGO_MINIFY_USE_STATIC = True
MINIFY_BUNDLES = {
    'css': {
        'flicks_css': (
            'css/main.css',
        ),
        'home_css': (
            'css/home.css',
        ),
        'videos': (
            'css/videos.css',
        ),
        'upload': (
            'css/upload.css',
        ),
    },
    'js': {
        'jquery': (
            'js/libs/jquery-1.7.1.min.js',
        ),
        'google_analytics': (
            'js/ga.js',
        ),
        'google_analytics_events': (
            'js/ga_event-tracking.js',
        ),
        'browserid': (
            'browserid/browserid.js',
        ),
        'flicks_js': (
            'js/init.js',
            'js/vote.js',
        ),
        'home_js': (
            'js/libs/jquery.waypoints.min.js',
            'js/libs/jquery.cycle2.min.js',
            'js/home.js',
        ),
        'persona_js': (
            'js/persona.js',
        ),
        'upload': (
            'js/libs/jquery.ui.widget.js',
            'js/libs/jquery.iframe-transport.js',
            'js/libs/jquery.fileupload.js',
            'js/upload.js',
        ),
        'profile': (
            'js/profile.js',
        ),
    }
}


# Promo video shortlinks
PROMO_VIDEOS = {
    'noir': {
        'en-us': '3q4s0q',
        'fr': '9j6k9j',
        'de': '7r0d1f',
        'es': '5m9i4w',
        'ja': '8r9w3d',
        'lij': '8y4r4v',
        'nl': '8d0f4b',
        'pl': '8u7s6j',
        'sl': '6e3t9x',
        'sq': '7c9p0d',
        'zh-cn': '0i8v1n',
        'zh-tw': '3r1o8k'
    },
    'dance': {
        'en-us': '3x8n2e',
        'fr': '2s8o4r',
        'de': '5i1u9r',
        'es': '8r3y6e',
        'ja': '5o7b0l',
        'lij': '7a8r6a',
        'nl': '0m4s3u',
        'pl': '4v1w8v',
        'sl': '6v3h2g',
        'sq': '0o5k7n',
        'zh-cn': '9w8d4k',
        'zh-tw': '5q2v4y'
    },
    'twilight': {
        'en-us': '6d9t7l',
        'fr': '4k0a3w',
        'de': '8n1f7u',
        'es': '0y9t0e',
        'ja': '3f9o1c',
        'lij': '5i0n9p',
        'nl': '8c5a2f',
        'pl': '3d8u9p',
        'sl': '9e2i0u',
        'sq': '3c8y0t',
        'zh-cn': '4w9f9x',
        'zh-tw': '3m0y4x'
    }
}
