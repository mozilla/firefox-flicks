from urllib import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

import jinja2
from tower import ugettext_lazy as _lazy

from flicks.base.util import use_lang


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


# L10n: Subject line for emails sent to users after their video has been moderated.
# L10n: Used for both approval and rejection emails.
EMAIL_SUBJECT = _lazy('Firefox Flicks: Your Recent Submission')


def send_approval_email(video):
    """
    Send email to the video's creator telling them that their video has been
    approved.
    """
    with use_lang(video.user.profile.locale):
        body = render_to_string('videos/2013/approval_email.html', {
            'user': video.user,
            'video': video
        })
    send_mail(EMAIL_SUBJECT, body, settings.DEFAULT_FROM_EMAIL,
              [video.user.email])


def send_rejection_email(video):
    """
    Send email to the video's creator telling them that their video has been
    rejected.
    """
    with use_lang(video.user.profile.locale):
        body = render_to_string('videos/2013/rejection_email.html', {
            'user': video.user
        })
    send_mail(EMAIL_SUBJECT, body, settings.DEFAULT_FROM_EMAIL,
              [video.user.email])


