# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'flicks_css': (
            'css/flicks_css/less.css',
            'css/flicks_css/main.css',
        ),
    },
    'js': {
        'flicks_js': (
            'js/libs/jquery-1.7.1.min.js',
            'js/libs/jquery.cookie.js',
            'js/init.js',
            'js/main.js',
        ),
    }
}

PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr', 'pt-BR')

# Defines the views served for root URLs.
ROOT_URLCONF = 'flicks.urls'

# Authentication
BROWSERID_CREATE_USER = True
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'django_browserid.context_processors.browserid_form',
]

# Paths that do not need a locale
SUPPORTED_NONLOCALES += ['notify']

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'flicks.base',
    'flicks.users',
    'flicks.videos',

    'django_browserid',
    'south',
]

AUTH_PROFILE_MODULE = 'flicks.UserProfile'

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

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

LOGGING = dict(loggers=dict(playdoh={'level': logging.DEBUG}))
