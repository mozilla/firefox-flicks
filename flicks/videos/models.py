from django.contrib.auth.models import User
from django.db import models

from funfactory.urlresolvers import reverse
from jinja2 import Markup
from tower import ugettext_lazy as _lazy

from flicks.videos.tasks import add_vote
from flicks.videos.vidly import embedCode


# Untranslated as they're only seen in the admin interface.
STATE_CHOICES = (
    ('unsent', 'Unsent'),
    ('processing', 'Processing'),
    ('complete', 'Complete'),
    ('error', 'Error')
)

CATEGORY_CHOICES = (
    ('thirty_spot', _lazy(':30 Spot')),
    ('animation', _lazy('Animation')),
    ('new_technology', _lazy('New Technology')),
    ('psa', _lazy('PSA'))
)

REGION_CHOICES = (
    ('americas', _lazy('The Americas')),
    ('europe', _lazy('Europe')),
    ('asia', _lazy('Asia, Oceania &amp; Australia')),
    ('africa', _lazy('Africa'))
)


class Video(models.Model):
    """Users can only have one video associated with
    their account.
    """
    # L10n: Title refers to the title of a video.
    title = models.CharField(max_length=100, blank=False,
                             verbose_name=_lazy(u'Title'))
    description = models.TextField(blank=True,
                                   verbose_name=_lazy(u'Description'))
    user = models.ForeignKey(User, blank=False)
    category = models.CharField(max_length=50, blank=False,
                                choices=CATEGORY_CHOICES,
                                verbose_name=_lazy(u'Category'))
    region = models.CharField(max_length=50, blank=False,
                              choices=REGION_CHOICES,
                              verbose_name=_lazy(u'Region'))

    upload_url = models.URLField(verify_exists=False, blank=False, default='',
                                 verbose_name=_lazy(u'Video URL'))
    shortlink = models.CharField(max_length=32, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default='unsent')

    votes = models.BigIntegerField(default=0)

    @property
    def embed_html(self):
        """Return the escaped HTML code to embed this video."""
        return Markup(embedCode(self.shortlink))

    @property
    def details_href(self):
        """Return the url for this video's details page."""
        return reverse('flicks.videos.details', kwargs={'video_id': self.id})

    def upvote(self):
        """Add an upvote to this video."""
        add_vote.delay(self)
