import base64
import hashlib
from contextlib import contextmanager

from django.contrib.auth.models import User
from django.utils.translation import get_language

import test_utils
from funfactory.urlresolvers import (get_url_prefix, Prefixer, reverse,
                                     set_url_prefix)
from nose.tools import ok_
from tower import activate

from flicks.users.models import UserProfile
from flicks.users.tests import mock_browserid


class TestCase(test_utils.TestCase):
    """Base class for Flicks test cases."""
    @contextmanager
    def activate(self, locale):
        """Context manager that temporarily activates a locale."""
        old_prefix = get_url_prefix()
        old_locale = get_language()
        rf = test_utils.RequestFactory()
        set_url_prefix(Prefixer(rf.get('/%s/' % (locale,))))
        activate(locale)
        yield
        set_url_prefix(old_prefix)
        activate(old_locale)

    def build_user(self, email=None, salt=None, login=False,
                   profile=True):
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

        return user

    def assert_viewname_url(self, url, viewname, locale='en-US'):
        """Compare a viewname's url to a given url."""
        with self.activate(locale):
            view_url = reverse(viewname)

        return ok_(url.endswith(view_url),
                   'URL Match failed: %s != %s' % (url, view_url))
