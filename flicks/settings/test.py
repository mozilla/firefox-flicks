# This file contains settings that apply only while the test suite is running.

SITE_URL = 'http://test.com'

VIDLY_USER_ID = '1234'
VIDLY_USER_KEY = 'asdf'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
