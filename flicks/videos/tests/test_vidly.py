import requests
from mock import patch
from nose.tools import eq_, ok_
from requests.exceptions import RequestException

from flicks.base.tests import TestCase
from flicks.videos import vidly
from flicks.videos.vidly import Success


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
    def _request(self, xml_params={}, status_code=200, side_effect=None,
                 **kwargs):
        """Make a request to vid.ly."""
        action = 'AddMedia'
        params = {'Source': {'SourceFile': 'http://test.com/source.mov',
                             'Output': 'webm'}}

        response_params = {'message': 'Test message', 'code': '2.1',
                           'source': 'http://test.com', 'shortlink': 'asdf'}
        response_params.update(xml_params)
        response_xml = RESPONSE_XML % response_params

        with patch.object(requests, 'post') as post:
            post.return_value = FakePostResponse(status_code, response_xml)
            post.side_effect = side_effect
            result = vidly.request(action, params, 'http://test.com', **kwargs)

        return result

    def test_no_user_info(self):
        """If a user id or password isn't provided, return None."""
        eq_(self._request(user_id=None, user_key=None), None)

    def test_connection_error(self):
        """If there is an error connecting to vid.ly, return None."""
        eq_(self._request(side_effect=RequestException), None)

    def test_non_200_response(self):
        """Any non-200 response from vid.ly returns None."""
        eq_(self._request(status_code=500), None)

    def test_basic_success(self):
        """Test normal conditions = success."""
        result = self._request()
        ok_(result['success'] is not None)
        eq_(result['errors'], [])


@patch('flicks.videos.vidly.ERROR_CODES', ['1'])
class AddMediaTests(TestCase):
    def _addMedia(self, source_file='file/path.mov',
                  notify_url='http://test.com'):
        """Call addMedia."""
        return vidly.addMedia(source_file, notify_url)

    @patch('flicks.videos.vidly.request')
    def test_connection_error(self, request):
        """An error connecting to vidly returns None."""
        request.return_value = None
        eq_(self._addMedia(), None)

    @patch('flicks.videos.vidly.ERROR_CODES', ['1'])
    @patch('flicks.videos.vidly.request')
    def test_vidly_error_code(self, request):
        """An erroneous status code returns None."""
        request.return_value = {'code': '1', 'errors': []}
        eq_(self._addMedia(), None)

    @patch('flicks.videos.vidly.ERROR_CODES', ['1'])
    @patch.object(vidly, 'request')
    def test_success_shortlink(self, request):
        """A successful response returns the shortlink."""
        request.return_value = {
            'code': '2.1',
            'msg': 'message',
            'success': Success('asdf', 'asdf'),
            'errors': []
        }

        eq_(self._addMedia(), 'asdf')
