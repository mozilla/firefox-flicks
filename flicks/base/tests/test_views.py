from django.conf import settings
from django.test.client import RequestFactory

from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.urls import handler500


class ViewTests(TestCase):
    def setUp(self):
        super(ViewTests, self).setUp()
        self.factory = RequestFactory()

    def test_robots_txt(self):
        with patch.object(settings, 'ENGAGE_ROBOTS', True):
            response = self.client.get('/robots.txt')
            eq_(response.content, 'User-agent: *\nAllow: /')

        with patch.object(settings, 'ENGAGE_ROBOTS', False):
            response = self.client.get('/robots.txt')
            eq_(response.content, 'User-agent: *\nDisallow: /')

    @patch('flicks.urls.render')
    def test_handler500(self, render):
        request = self.factory.get('/')
        request.in_overlay = True
        handler500(request)
        render.assert_called_with(request, 'videos/upload_error.html',
                                  status=500)

        request.in_overlay = False
        handler500(request)
        render.assert_called_with(request, '500.html', status=500)
