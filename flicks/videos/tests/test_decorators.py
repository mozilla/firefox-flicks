from django.http import HttpResponse
from django.test.client import RequestFactory

from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.videos.decorators import in_overlay


class TestInOverlay(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_basic(self):
        @in_overlay
        def blah(request, text):
            return HttpResponse(text)

        request = self.factory.get('/')
        response = blah(request, 'asdf')

        eq_(response.content, 'asdf')
        eq_(request.in_overlay, True)
