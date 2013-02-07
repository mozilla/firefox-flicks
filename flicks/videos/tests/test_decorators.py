from django.http import HttpResponse
from django.test.client import RequestFactory

from mock import patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCase
from flicks.videos import vimeo
from flicks.videos.decorators import in_overlay, vimeo_task


class TestInOverlay(TestCase):
    def setUp(self):
        super(TestInOverlay, self).setUp()
        self.factory = RequestFactory()

    def test_basic(self):
        @in_overlay
        def blah(request, text):
            return HttpResponse(text)

        request = self.factory.get('/')
        response = blah(request, 'asdf')

        eq_(response.content, 'asdf')
        eq_(request.in_overlay, True)


class VimeoTaskTests(TestCase):
    def test_basic(self):
        @vimeo_task
        def wrapped(a, b):
            raise vimeo.VimeoServiceError
            return a + b

        with patch.object(wrapped, 'retry', wraps=wrapped.retry) as retry:
            # When not being executed in a worker, retry just raises the
            # exception.
            with self.assertRaises(vimeo.VimeoServiceError):
                wrapped(1, 2)
            ok_(retry.called)
