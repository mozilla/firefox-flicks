from contextlib import nested

from django.conf import settings
from django.utils.unittest import skip

import requests
from elasticutils.tests import ESTestCase
from mock import patch
from nose.tools import eq_
from requests.exceptions import RequestException
from requests.models import Response

from flicks.base.tests import TestCase
from flicks.videos.forms import SearchForm, UploadForm
from flicks.videos.tests import build_video


class SearchFormTests(TestCase, ESTestCase):
    def _videos(self, **kwargs):
        params = {
            'search': '',
            'category': 'all',
            'region': 'all'
        }
        params.update(kwargs)
        f = SearchForm(params)
        return f.videos()

    def setUp(self):
        self.user = self.build_user()

    def test_search(self):
        """Test that basic title searching works."""
        with nested(build_video(self.user, title='Honey badger'),
                    build_video(self.user, title='Lolcats')) as (v1, v2):
            eq_(list(self._videos(search='badger')), [v1])

    def test_category_filter(self):
        """Test that search results can be filtered by category."""
        with nested(build_video(self.user, category='animation'),
                    build_video(self.user, category='psa')) as (v1, v2):
            eq_(list(self._videos(category='psa')), [v2])

    def test_region_filter(self):
        """Test that search results can be filtered by region."""
        with nested(build_video(self.user, region='america'),
                    build_video(self.user, region='europe')) as (v1, v2):
            eq_(list(self._videos(region='europe')), [v2])

    def test_invalid_search(self):
        """Test that an invalid form will return an empty list."""
        eq_(self._videos(category=''), [])


@skip
class UploadFormTests(TestCase):
    def _form(self, **kwargs):
        params = {
            'title': 'Test',
            'upload_url': 'http://test.com',
            'category': 'psa',
            'region': 'america',
            'agreement': True
        }
        params.update(kwargs)
        return UploadForm(params)

    def _response(self, status_code, content_type):
        response = Response()
        response.status_code = status_code
        if content_type is not None:
            response.headers['content-type'] = content_type
        return response

    @patch.object(requests, 'head')
    def test_request_exception(self, head):
        """If an error occurs while testing the upload url, the form is not
        valid.
        """
        head.side_effect = RequestException
        form = self._form()
        eq_(form.is_valid(), False)
        eq_(form.errors.keys(), ['upload_url'])

    @patch.object(requests, 'head')
    def test_invalid_status_code(self, head):
        """If the url returns a non-200 status code, the form is not valid."""
        head.return_value = self._response(404, '')
        form = self._form()
        eq_(form.is_valid(), False)
        eq_(form.errors.keys(), ['upload_url'])

    @patch.object(requests, 'head')
    @patch.object(settings, 'INVALID_VIDEO_CONTENT_TYPES', ['invalid/type'])
    def test_invalid_content_type(self, head):
        """If the url returns an invalid content-type, the form is not
        valid.
        """
        head.return_value = self._response(200, 'invalid/type; charset=UTF-8')
        form = self._form()
        eq_(form.is_valid(), False)
        eq_(form.errors.keys(), ['upload_url'])

    @patch.object(requests, 'head')
    def test_no_content_type(self, head):
        """If the url does not return a content-type, the form is valid."""
        head.return_value = self._response(200, None)
        form = self._form()
        eq_(form.is_valid(), True)

    @patch.object(requests, 'head')
    @patch.object(settings, 'INVALID_VIDEO_CONTENT_TYPES', ['invalid/type'])
    def test_success(self, head):
        """If the url returns a valid content-type and a 200 OK, the form is
        valid.
        """
        head.return_value = self._response(200, 'video/mpeg')
        form = self._form()
        eq_(form.is_valid(), True)
