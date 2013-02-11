import base64
import hashlib
from contextlib import contextmanager

from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

import test_utils
from django_browserid.tests import mock_browserid
from funfactory.urlresolvers import reverse
from nose.tools import ok_
from mock import patch

from flicks.base.tests.tools import lang_activate
from flicks.users.models import UserProfile


class SessionRequestFactory(RequestFactory):
    """RequestFactory that adds session data to requests."""
    def __init__(self, *args, **kwargs):
        super(SessionRequestFactory, self).__init__(*args, **kwargs)
        self.session_middleware = SessionMiddleware()

    def request(self, *args, **kwargs):
        request = super(SessionRequestFactory, self).request(*args, **kwargs)
        self.session_middleware.process_request(request)
        return request


class TestCase(test_utils.TestCase):
    """Base class for Flicks test cases."""
    def setUp(self):
        self.approval_patch = patch('flicks.videos.models.process_approval')
        self.approval_patch.start()

        self.deletion_patch = patch('flicks.videos.models.process_deletion')
        self.deletion_patch.start()

    def tearDown(self):
        self.approval_patch.stop()
        self.deletion_patch.stop()

    @contextmanager
    def activate(self, locale):
        with lang_activate(locale):
            yield

    def browserid_login(self, email):
        """Logs the test client in using BrowserID."""
        factory = SessionRequestFactory()
        with self.activate('en-US'):
            request = factory.get('/')
        with mock_browserid(email):
            self.client.login(request=request, assertion='asdf')

    def build_user(self, email=None, salt=None, login=False,
                   profile=True, **kwargs):
        """Retrieve a test user account for this class, creating one if it
        does not exist.

        kwargs:
           email: User's email
           salt: Used to generate username. For creating multiple users.
           login: If True, log the user in with the test client.
           profile: If True, create a UserProfile as well.
        """
        name = '%s_%s_%s' % (self.__class__.__name__, email, salt)
        username = base64.urlsafe_b64encode(
            hashlib.sha1(name).digest()).rstrip('=')
        email = email or '%s@test.com' % username

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username, email)

        if login:
            with mock_browserid(email):
                self.client.login()

        if profile:
            profile = UserProfile.objects.create(user=user)
            user.userprofile = profile
            user.save()

        if kwargs:
            User.objects.filter(pk=user.pk).update(**kwargs)

        return user

    def assert_viewname_url(self, url, viewname, locale='en-US'):
        """Compare a viewname's url to a given url."""
        with self.activate(locale):
            view_url = reverse(viewname)

        return ok_(url.endswith(view_url),
                   'URL Match failed: %s != %s' % (url, view_url))


class TestCache(object):
    def __init__(self):
        self.store = {}

    def get(self, id):
        return self.store.get(id, None)

    def set(self, id, value, timeout=None):
        self.store[id] = value

    def incr(self, id):
        self.store[id] += 1
        return self.store[id]

    def clear(self):
        self.store = {}
