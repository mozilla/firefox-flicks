import xml.etree.ElementTree as ET

import requests
from funfactory.urlresolvers import reverse
from mock import patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCase
from flicks.videos import vidly


RESPONSE_XML = """<?xml version="1.0"?>
<Response>
  <Message>%(message)s</Message>
  <MessageCode>%(code)s</MessageCode>
  <BatchID>0001</BatchID>
  <Success>
    <MediaShortLink>
      <SourceFile>%(source)s</SourceFile>
      <ShortLink>%(shortlink)s</ShortLink>
    </MediaShortLink>
  </Success>
</Response>
"""


class FakePostResponse(object):
    """Fakes a requests response object."""
    def __init__(self, status_code, xml):
        self.status_code = status_code
        self.content = xml


class RequestTests(TestCase):
    def _request(self, xml_params={}, status_code=200, **kwargs):
        """Make a request to vid.ly."""
        action = 'AddMedia'
        params = {'Source': {'SourceFile': 'http://test.com/source.mov',
                             'Output': 'webm'}}
        with self.activate('en-US'):
            notify = reverse('flicks.videos.notify')

        response_params = {'message': 'Test message', 'code': '2.1',
                           'source': 'http://test.com', 'shortlink': 'asdf'}
        response_params.update(xml_params)
        response_xml = RESPONSE_XML % response_params

        with patch.object(requests, 'post') as post:
            post.return_value = FakePostResponse(status_code, response_xml)
            result = vidly.request(action, params, notify, **kwargs)

        return result

    def test_no_user_info(self):
        """If a user id or password isn't provided, return None."""
        eq_(self._request(user_id=None, user_key=None), None)

    def test_non_200_response(self):
        """Any non-200 response from vid.ly returns None."""
        eq_(self._request(status_code=500), None)

    def test_basic_success(self):
        """Test normal conditions = success."""
        result = self._request()
        ok_(result['success'] is not None)
        eq_(result['errors'], None)


@patch('flicks.videos.vidly.ERROR_CODES', ['1'])
class AddMediaTests(TestCase):
    def _addMedia(self, response, source_file='file/path.mov',
                  notify_url='http://test.com'):
        """Call addMedia and mock the return value for request."""
        with patch('flicks.videos.vidly.request') as request:
            request.return_value = response
            result = vidly.addMedia(source_file, notify_url)
        return result

    def test_connection_error(self):
        """An error connecting to vidly returns None."""
        eq_(self._addMedia(None), None)

    @patch('flicks.videos.vidly.ERROR_CODES', ['1'])
    def test_vidly_error_code(self):
        """An erroneous status code returns None."""
        eq_(self._addMedia({'code': '1', 'errors': []}), None)

    def test_success_shortlink(self):
        """A successful response returns the shortlink."""
        success = ET.Element('Success')
        media_shortlink = ET.SubElement(success, 'MediaShortLink')
        ET.SubElement(media_shortlink, 'ShortLink').text = 'asdf'

        eq_(self._addMedia({'success': success, 'code': '2'}), 'asdf')
