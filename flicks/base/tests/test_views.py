from datetime import date

from django.conf import settings
from django.test.client import RequestFactory

from funfactory.urlresolvers import reverse
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
        request.upload_process = True
        handler500(request)
        render.assert_called_with(request, 'videos/upload_error.html',
                                  status=500)

        request.upload_process = False
        handler500(request)
        render.assert_called_with(request, '500.html', status=500)

    @patch('flicks.base.views.carousel.get_slides')
    def test_home_promo_preview(self, get_slides):
        """
        If a date is passed to the homepage as a querystring argument, show
        promos for that date instead of the current date.
        """
        with self.activate('en-US'):
            self.client.get(reverse('flicks.base.home'), {'date': '2012-4-15'})
        get_slides.assert_called_with(date(2012, 4, 15))

    @patch('flicks.base.views.carousel.get_slides')
    def test_home_promo_preview_invalid(self, get_slides):
        """
        If an invalid date is passed to the homepage as a querystring argument,
        don't pass a date to get_slides.
        """
        with self.activate('en-US'):
            self.client.get(reverse('flicks.base.home'), {'date': 'invalid'})
        get_slides.assert_called_with(None)
