from django.conf import settings

import commonware
import requests
from requests_oauthlib import OAuth1


logger = commonware.log.getLogger('f.videos.vimeo')


class VimeoServiceError(Exception):
    pass


class VimeoTicketInvalid(Exception):
    pass


def _vimeo_request(vimeo_method, request_method, **data):
    oauth = OAuth1(settings.VIMEO_CLIENT_KEY,
                   client_secret=settings.VIMEO_CLIENT_SECRET,
                   resource_owner_key=settings.VIMEO_RESOURCE_OWNER_KEY,
                   resource_owner_secret=settings.VIMEO_RESOURCE_OWNER_SECRET)
    url = 'http://vimeo.com/api/rest/v2?method={0}'.format(vimeo_method)
    data['format'] = 'json'

    try:
        response = requests.request(request_method, url, auth=oauth, data=data)
    except requests.RequestException, e:
        logger.error('Error connecting to Vimeo: {0}'.format(e))
        raise VimeoServiceError(e)

    return response.json()


def _ticket_request(vimeo_method, request_method, error_msg=None, **data):
    response = _vimeo_request(vimeo_method, request_method, **data)
    if response['stat'] == 'fail':
        err = response['err']
        ticket_id = data.get('ticket_id', '')

        # Log failure if it is not because the ticket is invalid (code 702)
        if err['code'] == '702':
            raise VimeoTicketInvalid('Invalid ticket `{0}`'.format(ticket_id))
        else:
            msg = error_msg.format(ticket_id=ticket_id,
                                   code=err.get('code', ''),
                                   msg=err.get('msg', ''),
                                   expl=err.get('expl', ''))
            logger.error(msg)
            raise VimeoServiceError(msg)

    return response


def get_new_ticket():
    """Request a new upload ticket from Vimeo."""
    response = _vimeo_request('vimeo.videos.upload.getTicket', 'POST',
                              upload_method='post')
    if response['stat'] == 'fail':
        err = response['err']
        logger.error('Error retrieving upload ticket: <{code} {msg}> {expl}'
                     .format(code=err.get('code', ''), msg=err.get('msg', ''),
                             expl=err.get('expl', '')))
        return False
    return response['ticket']


def is_ticket_valid(ticket_id):
    """Check if an upload ticket is still valid."""
    try:
        _ticket_request(
            'vimeo.videos.upload.checkTicket', 'POST', ticket_id=ticket_id,
            error_msg='Error checking if ticket `{ticket_id}` is valid: '
                      '<{code} {msg}> {expl}')
        return True
    except VimeoTicketInvalid:
        return False


def verify_chunks(ticket_id, expected_size):
    """
    Verify that the entire video file made it to Vimeo.

    :param ticket_id:
        ID for the upload ticket.
    :param expected_size:
        Expected video file size, in bytes.
    """
    response = _ticket_request(
        'vimeo.videos.upload.verifyChunks', 'POST', ticket_id=ticket_id,
        error_msg='Error verifying chunks for ticket`{ticket_id}`: '
                  '<{code} {msg}> {expl}')
    # Apparently verifyChunks doesn't give a list of chunks if there's only
    # one chunk, and there's no reference online to show otherwise.
    size = int(response['ticket']['chunks']['chunk']['size'])
    return size == int(expected_size)


def complete_upload(ticket_id, filename):
    """Mark an upload as complete and submit it for processing."""
    response = _ticket_request('vimeo.videos.upload.complete', 'POST',
        ticket_id=ticket_id, filename=filename,
        error_msg='Error completing upload for ticket `{ticket_id}`: '
                  '<{code} {msg}> {expl}')
    return response['ticket']
