from django.conf import settings

import commonware
import requests
from requests_oauthlib import OAuth1

from flicks.videos.decorators import vimeo_task


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


def _video_request(vimeo_method, request_method, error_msg=None, **data):
    response = _vimeo_request(vimeo_method, request_method, **data)
    if response['stat'] == 'fail':
        err = response['err']
        video_id = data.get('video_id', '')
        msg = error_msg.format(video_id=video_id,
                               code=err.get('code', ''),
                               msg=err.get('msg', ''),
                               expl=err.get('expl', ''))
        raise VimeoServiceError(msg)
    return response


@vimeo_task
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


@vimeo_task
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


@vimeo_task
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


@vimeo_task
def complete_upload(ticket_id, filename):
    """Mark an upload as complete and submit it for processing."""
    msg = ('Error completing upload for ticket `{{ticket_id}}` with filename '
           '`{0}`: <{{code}} {{msg}}> {{expl}}'.format(filename))
    response = _ticket_request('vimeo.videos.upload.complete', 'POST',
                               ticket_id=ticket_id, filename=filename,
                               error_msg=msg)
    return response['ticket']


@vimeo_task
def set_title(video_id, title):
    """Set the title of a video."""
    _video_request('vimeo.videos.setTitle', 'POST', video_id=video_id,
                   title=title.encode('ascii', 'xmlcharrefreplace'),
                   error_msg='Error setting title for video {video_id}: '
                             '<{code} {msg}> {expl}')


@vimeo_task
def set_description(video_id, description):
    """Set the description of a video."""
    _video_request('vimeo.videos.setDescription', 'POST', video_id=video_id,
                   description=description.encode('ascii', 'xmlcharrefreplace'),
                   error_msg='Error setting description for video {video_id}: '
                             '<{code} {msg}> {expl}')


@vimeo_task
def add_to_channel(video_id, channel_id):
    """Add a video to a channel."""
    _video_request('vimeo.channels.addVideo', 'POST', video_id=video_id,
                   channel_id=channel_id,
                   error_msg='Error setting channel for video {video_id}: '
                             '<{code} {msg}> {expl}')


@vimeo_task
def add_tags(video_id, tags):
    """Add tags to a video."""
    _video_request('vimeo.videos.addTags', 'POST', video_id=video_id,
                   tags=','.join(tags),
                   error_msg='Error adding tags for video {video_id}: '
                             '<{code} {msg}> {expl}')


@vimeo_task
def set_privacy(video_id, privacy, password=None):
    """Set privacy options on a video."""
    _video_request('vimeo.videos.setPrivacy', 'POST', video_id=video_id,
                   privacy=privacy, password=password,
                   error_msg=('Error setting privacy for video {video_id}: '
                              '<{code} {msg}> {expl}'))


@vimeo_task
def delete_video(video_id):
    """Permanently delete a video."""
    _video_request('vimeo.videos.delete', 'POST', video_id=video_id,
                   error_msg=('Error deleting video {video_id}: <{code} {msg}> '
                              '{expl}'))


@vimeo_task
def get_thumbnail_urls(video_id):
    """Get thumbnail urls for a video."""
    response = _video_request('vimeo.videos.getThumbnailUrls', 'POST',
                              video_id=video_id,
                              error_msg=('Error getting thumbnails for video '
                                         '{video_id}: <{code} {msg}> {expl}'))
    return response['thumbnails']['thumbnail']
