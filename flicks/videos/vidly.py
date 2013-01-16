import xml.etree.ElementTree as ET
from collections import namedtuple

from django.conf import settings

import commonware.log
import requests
from requests.exceptions import RequestException


_API_URL = 'https://m.vid.ly/api/'
ERROR_CODES = ['1.1', '1.2', '2.2', '2.3']  # Vidly error codes
log = commonware.log.getLogger('f.vidly')


VIDLY_API_URL = getattr(settings, 'VIDLY_API_URL', _API_URL)
VIDLY_USER_ID = getattr(settings, 'VIDLY_USER_ID', None)
VIDLY_USER_KEY = getattr(settings, 'VIDLY_USER_KEY', None)
VIDLY_OUTPUT_FORMATS = getattr(settings, 'VIDLY_OUTPUT_FORMATS', ['webm'])
VIDLY_OUTPUT_SIZE = getattr(settings, 'VIDLY_OUTPUT_SIZE', '640x480')

POSTER_URL = 'https://d3fenhwk93s16g.cloudfront.net/%s/poster.jpg'


Error = namedtuple('Error', ['shortlink', 'code', 'name', 'desc'])
Success = namedtuple('Success', ['shortlink', 'source'])
Task = namedtuple('Task', ['shortlink', 'finished'])


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
    log.error('Vidly Request: %s' % xml_str)

    try:
        res = requests.post(api_url, data={'xml': xml_str})
    except RequestException, e:
        log.error('Error connecting to Vidly: %s' % e)
        return None

    if res.status_code != 200:
        log.error('Vidly returned non-200 response: %s' % res.status_code)
        return None

    # Parse response
    log.error('Vidly Response: %s' % res.content)
    response_elem = ET.fromstring(res.content)
    message = response_elem.find('Message')
    message_code = response_elem.find('MessageCode')

    success = _parse_success(response_elem.find('Success'))
    errors = _parse_errors(response_elem.find('Errors'))

    return {'code': message_code.text,
            'msg': message.text,
            'success': success,
            'errors': errors}


def _parse_success(success_elem):
    """Parse success XML"""
    if success_elem is None:
        return None
    elem = success_elem.find('MediaShortLink')
    return Success(elem.find('ShortLink').text, elem.find('SourceFile').text)


def _parse_errors(errors_elem):
    """Parse error XML."""
    errors = []
    if errors_elem is not None:
        for error in errors_elem.findall('Error'):
            # If there is no shortlink, we have no use for the error.
            if error.find('MediaShortLink') is None:
                continue

            errors.append(Error(error.find('MediaShortLink').text,
                                error.find('ErrorCode').text,
                                error.find('ErrorName').text,
                                error.find('Description').text))

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
    elif response['code'] in ERROR_CODES or response['success'] is None:
        for error in response['errors']:
            log.error('Error converting media: %s; %s' % (source_file, error))
        return None

    return response['success'].shortlink


def parseNotify(request):
    """Parse notification from vid.ly that video conversion is complete."""
    xml_str = request.POST.get('xml', None)
    if xml_str is None:
        return None

    log.error('Vidly Notification: %s' % xml_str)
    response = ET.fromstring(xml_str)

    # Parse tasks (usually means success) and errors.
    errors = _parse_errors(response.find('Errors'))
    tasks = _parse_result(response.find('Result'))
    return {'tasks': tasks, 'errors': errors}


def _parse_result(result_elem):
    """Parse result XML and return a list of tasks."""
    tasks = []
    if result_elem is not None:
        for task in result_elem.findall('Task'):
            tasks.append(Task(task.find('MediaShortLink').text,
                              task.find('Status').text == 'Finished'))
    return tasks


def embedCode(shortlink, width, height):
    """Generate escaped HTML code to embed a vid.ly video."""
    poster = POSTER_URL % shortlink
    return """
    <iframe frameborder="0"
            name="vidly-frame"
            width="%(width)s"
            height="%(height)s"
            src="https://vid.ly/embeded.html?link=%(shortlink)s&autoplay=false">
      <a target='_blank' href='http://vid.ly/%(shortlink)s'>
        <img src='%(poster)s'>
      </a>
    </iframe>
    """ % {'shortlink': shortlink, 'poster': poster, 'width': width,
           'height': height}
