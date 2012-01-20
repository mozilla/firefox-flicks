from django.contrib.auth.models import User
from django.db import models

from jinja2 import Markup

from flicks.videos.vidly import embedCode


# Untranslated as they're only seen in the admin interface.
STATE_CHOICES = (
    ('unsent', 'Unsent'),
    ('processing', 'Processing'),
    ('complete', 'Complete'),
    ('error', 'Error')
)


class Video(models.Model):
    """Users can only have one video associated with
    their account.
    """
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, blank=False)
    category = models.CharField(max_length=50, blank=False, default='')
    region = models.CharField(max_length=50, blank=False, default='')

    upload_url = models.URLField(verify_exists=False, blank=False, default='')
    shortlink = models.CharField(max_length=32, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default='unsent')

    @property
    def embed_html(self):
        """Return the escaped HTML code to embed this video."""
        return Markup(embedCode(self.shortlink))
