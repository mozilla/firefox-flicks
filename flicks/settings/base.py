# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'flicks_css': (
            'css/less.css',
            'css/main.css',
        ),
    },
    'js': {
        'flicks_js': (
            'js/libs/jquery-1.7.1.min.js',
            'js/libs/jquery.cookie.js',
            'js/libs/webtrends.js',
            'js/init.js',
        ),
        'video_details': (
            'js/libs/script.js',
            'js/vote.js',
            'js/views.js',
            'js/share.js',
        ),
    }
}

PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr', 'lij', 'nl', 'pl', 'pt-BR', 'sl',
                  'zh-CN')

# Defines the views served for root URLs.
ROOT_URLCONF = 'flicks.urls'

# Authentication
BROWSERID_CREATE_USER = True
LOGIN_URL = '/'
LOGIN_REDIRECT = 'flicks.videos.upload'
LOGIN_REDIRECT_FAILURE = 'flicks.base.home'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'django_browserid.context_processors.browserid_form',
]

# Paths that do not need a locale
SUPPORTED_NONLOCALES += ['notify']

# Gravatar Settings
GRAVATAR_URL = 'https://secure.gravatar.com'
DEFAULT_GRAVATAR = MEDIA_URL + 'img/anon_user.png'

# Vote settings
VOTE_COOKIE_AGE = 157680000  # 5 years

# Elasticutils
ES_DISABLED = True

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'flicks.base',
    'flicks.users',
    'flicks.videos',

    'csp',
    'django_browserid',
    'south',
]

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + [
    'commonware.response.middleware.StrictTransportMiddleware',
    'csp.middleware.CSPMiddleware',
]

AUTH_PROFILE_MODULE = 'flicks.UserProfile'

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('**/flicks/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/flicks/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template')
    ],
}

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

# Always generate a CSRF token for anonymous users
ANON_ALWAYS = True

# Promo video shortlinks
PROMO_VIDEOS = {
    'noir': {
        'en-us': '3q4s0q'
    },
    'dance': {
        'en-us': '3x8n2e'
    },
    'twilight': {
        'en-us': '6d9t7l'
    }
}

# Email Settings
DEFAULT_FROM_EMAIL = 'firefoxflicks@mozilla.com'
FACEBOOK_LINK = 'http://www.facebook.com/FirefoxFlicks'
TWITTER_LINK = 'https://twitter.com/#!/firefoxflicks'

# Bit.ly API settings
BITLY_API_SHORTEN = 'https://api-ssl.bitly.com/v3/shorten'
BITLY_API_KEY = ''
BITLY_API_LOGIN = ''

# Secure Cookies
SESSION_COOKIE_SECURE = True

# Django-CSP
CSP_IMG_SRC = ("'self'",
               'http://cf.cdn.vid.ly',
               'https://www.gravatar.com',
               'https://secure.gravatar.com',
               'https://statse.webtrendslive.com',)
CSP_STYLE_SRC = ("'self'",
                 'https://fonts.googleapis.com')
CSP_FONT_SRC = ("'self'",
                'https://themes.googleusercontent.com',)
CSP_SCRIPT_SRC = ("'self'",
                  'http://browserid.org',
                  'https://browserid.org',
                  'https://platform.twitter.com',
                  'https://connect.facebook.net',
                  'https://statse.webtrendslive.com',)
CSP_FRAME_SRC = ('http://s.vid.ly',
                 'http://platform.twitter.com',
                 'https://platform.twitter.com',
                 'https://www.facebook.com',)
CSP_OPTIONS = ('eval-script',)
