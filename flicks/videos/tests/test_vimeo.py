import requests
from mock import ANY, Mock, patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCase
from flicks.videos import vimeo


class TestVimeo(TestCase):
    @patch('flicks.videos.vimeo.requests.request')
    def test_vimeo_request_basic(self, mock_request):
        mock_response = Mock()
        mock_request.return_value = mock_response
        response = vimeo._vimeo_request('method', 'GET', mydata='blah')

        mock_request.assert_called_with(
            'GET', 'http://vimeo.com/api/rest/v2?method=method', auth=ANY,
            data={'mydata': 'blah', 'format': 'json'})
        mock_response.json.assert_called_with()
        eq_(mock_response.json(), response)

    @patch('flicks.videos.vimeo.requests.request')
    def test_vimeo_request_error(self, mock_request):
        """If there is an error contacting Vimeo, raise a VimeoServiceError."""
        mock_request.side_effect = requests.RequestException
        with self.assertRaises(vimeo.VimeoServiceError):
            vimeo._vimeo_request('method', 'GET', mydata='blah')

    @patch('flicks.videos.vimeo._vimeo_request')
    def test_ticket_request_basic(self, _vimeo_request):
        return_response = {'stat': 'ok', 'ticket': 'blah'}
        _vimeo_request.return_value = return_response
        response = vimeo._ticket_request('method', 'POST', some='data')

        _vimeo_request.assert_called_with('method', 'POST', some='data')
        eq_(response, return_response)

    @patch('flicks.videos.vimeo._vimeo_request')
    def test_ticket_request_invalid_ticket(self, _vimeo_request):
        """
        If the request fails with a 702 error code, raise VimeoTicketInvalid.
        """
        _vimeo_request.return_value = {'stat': 'fail', 'err': {'code': '702'}}
        with self.assertRaises(vimeo.VimeoTicketInvalid):
            vimeo._ticket_request('method', 'POST', some='data')

    @patch('flicks.videos.vimeo._vimeo_request')
    @patch('flicks.videos.vimeo.logger')
    def test_ticket_request_error(self, logger, _vimeo_request):
        """
        If the request fails with an error code besides 702, log it and raise
        VimeoServiceError.
        """
        _vimeo_request.return_value = {
            'stat': 'fail',
            'err': {'code': '701', 'msg': 'test msg', 'expl': 'test_expl'}
        }

        with self.assertRaises(vimeo.VimeoServiceError):
            vimeo._ticket_request('method', 'POST', ticket_id='test',
                                  error_msg='{ticket_id} {code} {msg} {expl}')
        logger.error.assert_called_with('test 701 test msg test_expl')

    @patch('flicks.videos.vimeo._vimeo_request')
    def test_get_new_ticket(self, _vimeo_request):
        _vimeo_request.return_value = {'stat': 'ok', 'ticket': 'returnvalue'}

        eq_(vimeo.get_new_ticket(), 'returnvalue')
        _vimeo_request.assert_called_with('vimeo.videos.upload.getTicket',
                                          'POST', upload_method='post')

    @patch('flicks.videos.vimeo._vimeo_request')
    @patch('flicks.videos.vimeo.logger')
    def test_get_new_ticket_fail(self, logger, _vimeo_request):
        """If retrieving a new ticket fails, return False."""
        _vimeo_request.return_value = {
            'stat': 'fail',
            'err': {'code': '701', 'msg': 'test msg', 'expl': 'test_expl'}
        }

        eq_(vimeo.get_new_ticket(), False)
        ok_(logger.error.called)

    @patch('flicks.videos.vimeo._ticket_request')
    def test_is_ticket_valid(self, _ticket_request):
        """If VimeoTicketInvalid is not thrown, return True."""
        _ticket_request.return_value = {'stat': 'ok'}
        eq_(vimeo.is_ticket_valid('id'), True)

    @patch('flicks.videos.vimeo._ticket_request')
    def test_is_ticket_valid_failure(self, _ticket_request):
        """If VimeoTicketInvalid is thrown, return False."""
        _ticket_request.side_effect = vimeo.VimeoTicketInvalid
        eq_(vimeo.is_ticket_valid('id'), False)

    @patch('flicks.videos.vimeo._ticket_request')
    def test_verify_chunks(self, _ticket_request):
        """If the size given by Vimeo matches the expected size, return True."""
        _ticket_request.return_value = {'ticket': {'chunks': {'chunk': {
            'size': '4'
        }}}}
        eq_(vimeo.verify_chunks('id', 4), True)

    @patch('flicks.videos.vimeo._ticket_request')
    def test_verify_chunks_no_match(self, _ticket_request):
        """
        If the size given by Vimeo does not match the expected size, return
        False.
        """
        _ticket_request.return_value = {'ticket': {'chunks': {'chunk': {
            'size': '3'
        }}}}
        eq_(vimeo.verify_chunks('id', 4), False)

    @patch('flicks.videos.vimeo._ticket_request')
    def test_complete_upload(self, _ticket_request):
        """Return the ticket given by Vimeo after completing the upload."""
        _ticket_request.return_value = {'stat': 'ok', 'ticket': {'some': 'dat'}}
        eq_(vimeo.complete_upload('id', 'filename'), {'some': 'dat'})
