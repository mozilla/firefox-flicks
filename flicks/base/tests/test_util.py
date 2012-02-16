from contextlib import nested
from functools import partial

from django.conf import settings

import requests
from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.base.util import (absolutify, generate_bitly_link,
                              get_object_or_none, redirect)
from flicks.videos.models import Video
from flicks.videos.tests import build_video


@patch.object(settings, 'SITE_URL', 'http://test.com')
class AbsolutifyTests(TestCase):
    def test_basic(self):
        """Test that the domain is added correctly."""
        eq_(absolutify('test'), 'http://test.com/test')

    def test_with_slash(self):
        """A path starting with a slash does not have an extra slash."""
        eq_(absolutify('/test/path'), 'http://test.com/test/path')


class TestRedirect(TestCase):
    urls = 'flicks.base.tests.urls'

    def test_basic(self):
        with self.activate('en-US'):
            response = redirect('mock_view')
        eq_(response.status_code, 302)
        eq_(response['Location'], '/en-US/mock_view')

    def test_permanent(self):
        with self.activate('en-US'):
            response = redirect('mock_view', permanent=True)
        eq_(response.status_code, 301)
        eq_(response['Location'], '/en-US/mock_view')


class TestGetObjectOrNone(TestCase):
    def setUp(self):
        self.user = self.build_user()

    def test_does_not_exist(self):
        """Return None if no matching video exists."""
        value = get_object_or_none(Video, title='Does not exist')
        eq_(value, None)

    def test_multiple_objects_returned(self):
        """Return None if multiple objects are returned."""
        mkvideo = partial(build_video, self.user, title='multiple')
        with nested(mkvideo(), mkvideo()):
            value = get_object_or_none(Video, title='multiple')
            eq_(value, None)

    def test_exists(self):
        """If no exceptions occur, return the matched object."""
        with build_video(self.user, title='exists') as video:
            value = get_object_or_none(Video, title='exists')
            eq_(value, video)


class GenerateBitlyLinkTests(TestCase):
    @patch.object(requests, 'get')
    def test_error_return_none(self, get):
        """If requests throws an exception, return None."""
        # Test a non-200 status code
        get.return_value = requests.Response()
        get.return_value.status_code = 500
        eq_(generate_bitly_link('test'), None)

        # Test an exception
        get.side_effect = requests.exceptions.RequestException
        eq_(generate_bitly_link('test'), None)
