from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test.client import RequestFactory

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.decorators import profile_required
from flicks.users.tests import UserFactory, UserProfileFactory


class TestProfileRequired(TestCase):
    def setUp(self):
        super(TestProfileRequired, self).setUp()
        self.factory = RequestFactory()

    def test_no_user(self):
        """
        If the given request has no logged-in user, return a redirect to
        LOGIN_URL.
        """
        @profile_required
        def view(request):
            return HttpResponse('asdf')

        request = self.factory.get('/someurl')
        request.user = AnonymousUser()
        with self.settings(LOGIN_URL='/test/url'):
            response = view(request)
            redirects_(response, '/test/url?next=/someurl')

    def test_no_user_with_login_url(self):
        """
        If the given request has no logged-in user, return a redirect to the
        given login_url.
        """
        @profile_required(login_url='/test/url2')
        def view(request):
            return HttpResponse('asdf')

        request = self.factory.get('/someurl')
        request.user = AnonymousUser()
        with self.settings(LOGIN_URL='/test/url'):
            response = view(request)
            redirects_(response, '/test/url2?next=/someurl')

    def test_no_profile(self):
        """
        If the user has no profile, return a redirect to flicks.users.profile.
        """
        @profile_required
        def view(request):
            return HttpResponse('asdf')

        request = self.factory.get('/someurl')
        request.user = UserFactory()
        response = view(request)
        redirects_(response, 'flicks.users.profile')

    def test_has_profile(self):
        """
        If the user has a profile, continue to the view.
        """
        @profile_required
        def view(request):
            return HttpResponse('asdf')

        request = self.factory.get('/someurl')
        request.user = UserProfileFactory().user
        response = view(request)
        self.assertContains(response, 'asdf')
