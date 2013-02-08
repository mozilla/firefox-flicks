from urllib import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

import jinja2


def vidly_embed_code(shortlink, width=600, height=337):
    """Return embed HTML for a vid.ly video."""
    poster = 'https://d3fenhwk93s16g.cloudfront.net/%s/poster.jpg' % shortlink
    html = render_to_string('videos/2012/vidly_embed.html', {
        'shortlink': shortlink,
        'poster': poster,
        'width': width,
        'height': height
    })
    return jinja2.Markup(html)


def vimeo_embed_code(vimeo_id, width=600, height=338, elem_class='video'):
    """Return embed HTML for a Vimeo video."""
    url = ('https://player.vimeo.com/video/{video_id}'
           .format(video_id=vimeo_id))
    url = '?'.join([url, urlencode({
        'title': 0,
        'byline': 0,
        'portrait': 0,
        'color': 'ffffff',
        'autoplay': 0
    })])

    return ('<iframe class="{elem_class}" src="{url}" width="{width}" '
            'height="{height}" frameborder="0"></iframe>'.strip().format(
            url=url, width=width, height=height, elem_class=elem_class))


def send_approval_email(video):
    """
    Send email to the video's creator telling them that their video has been
    approved.
    """
    # TODO: Add final copy.
    subject = 'Your video has been approved!'
    body = render_to_string('videos/2013/approval_email.html', {
        'name': video.user.profile.display_name,
        'video': video
    })
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [video.user.email])


def send_decline_email(video):
    """
    Send email to the video's creator telling them that their video has been
    declined.
    """
    # TODO: Add final copy.
    subject = 'Your video has been declined'
    body = render_to_string('videos/2013/decline_email.html', {
        'name': video.user.profile.display_name
    })
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [video.user.email])


