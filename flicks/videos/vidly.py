import xml.etree.ElementTree as ET

from django.conf import settings

import commonware.log
import requests


_API_URL = 'https://m.vid.ly/api/'
ERROR_CODES = ['1.1', '1.2', '2.2', '2.3']  # Vidly error codes
log = commonware.log.getLogger('f.vidly')


VIDLY_API_URL = getattr(settings, 'VIDLY_API_URL', _API_URL)
VIDLY_USER_ID = getattr(settings, 'VIDLY_USER_ID', None)
VIDLY_USER_KEY = getattr(settings, 'VIDLY_USER_KEY', None)
VIDLY_OUTPUT_FORMATS = getattr(settings, 'VIDLY_OUTPUT_FORMATS', ['webm'])
VIDLY_OUTPUT_SIZE = getattr(settings, 'VIDLY_OUTPUT_SIZE', '640x480')


def request(action, params, notify_url, user_id=VIDLY_USER_ID,
            user_key=VIDLY_USER_KEY, api_url=VIDLY_API_URL):
    """Call the vid.ly API with the supplied parameters."""
    if user_id is None or user_key is None:
        log.warning('You are missing a user id and/or key for vidly. You '
                    'should pass these to the function you called or specify '
                    'them in settings.VIDLY_USER_ID and '
                    'settings.VIDLY_USER_KEY.')
        return None

    # Build XML Query
    query = ET.Element('Query')
    ET.SubElement(query, 'Action').text = action
    ET.SubElement(query, 'UserID').text = user_id
    ET.SubElement(query, 'UserKey').text = user_key
    ET.SubElement(query, 'Notify').text = notify_url

    _build_param_xml(query, params)

    # Getting an xml version header out of ElementTree is tough.
    # It's easier for our use case to just prepend it.
    xml_str = '<?xml version="1.0"?>%s' % ET.tostring(query)
    log.info('Vidly Request: %s' % xml_str)

    res = requests.post(api_url, data={'xml': xml_str})
    if res.status_code != 200:
        log.warning('Vidly returned non-200 response: %s' % res.status_code)
        return None

    # Parse response
    log.info('Vidly Response: %s' % res.content)
    response_elem = ET.fromstring(res.content)
    message = response_elem.find('Message')
    message_code = response_elem.find('MessageCode')
    success = response_elem.find('Success')

    errors_elem = response_elem.find('Errors')
    errors = _parse_errors(errors_elem) if errors_elem is not None else None

    return {'code': message_code.text,
            'msg': message.text,
            'success': success,
            'errors': errors}


def _parse_errors(errors_elem):
    """Parse error XML."""
    errors = []
    for error in errors_elem.findall('Error'):
        errors.append('Code: %s, Name: %s, Description: %s, Suggestion: %s' % (
            error.find('ErrorCode').text, error.find('ErrorName').text,
            error.find('Description').text, error.find('Suggestion').text
        ))

    return errors


def _build_param_xml(parent, params):
    """Builds a nested XML structure from nested maps."""
    try:
        for key, value in params.items():
            elem = ET.SubElement(parent, key)
            _build_param_xml(elem, value)
    except AttributeError:
        # Not a map, treat it as a string
        parent.text = params


def addMedia(source_file, notify_url):
    """Send a media file to vid.ly for conversion."""
    params = {'Source': {'SourceFile': source_file,
                         'Output': ','.join(VIDLY_OUTPUT_FORMATS),
                         'Size': VIDLY_OUTPUT_SIZE}}

    response = request('AddMedia', params, notify_url)
    if response is None:
        log.error('Error connecting to vid.ly with file: %s' % source_file)
        return None
    elif response['code'] in ERROR_CODES:
        for error in response['errors']:
            log.error('Error converting media: %s; %s' % (source_file, error))
        return None

    success = response['success']
    shortlink = success.find('MediaShortLink').find('ShortLink').text

    return shortlink


def parseNotify(request):
    """Parse notification from vid.ly that video conversion is complete."""
    xml_str = request.POST.get('xml', None)
    if xml_str is None:
        return None

    log.info('Vidly Notification: %s' % xml_str)
    result = ET.fromstring(xml_str).find('Result')

    # Vid.ly sends two notifications; one as soon as the video is sent, and one
    # after the video finishes processing. We really only care about the second
    # one, so here we ignore the first.
    if result is None:
        return None

    task = result.find('Task')
    return {'user_id': task.find('UserID').text,
            'shortlink': task.find('MediaShortLink').text,
            'status': task.find('Status').text}


def embedCode(shortlink):
    """Generate escaped HTML code to embed a vid.ly video."""
    return """
    <iframe frameborder="0"
            name="vidly-frame"
            src="http://s.vid.ly/embeded.html?link=%(shortlink)s&autoplay=false">
      <a target='_blank' href='http://vid.ly/%(shortlink)s'>
        <img src='http://cf.cdn.vid.ly/%(shortlink)s/poster.jpg' />
      </a>
    </iframe>
    """ % {'shortlink': shortlink}
