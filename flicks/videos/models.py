from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string

import jinja2
from caching.base import CachingManager, CachingMixin
from tower import ugettext as _, ugettext_lazy as _lazy


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
    ('america', _lazy('North America')),
    ('latin_america', _lazy('Latin America')),
    ('europe', _lazy('Europe')),
    ('asia_africa_australia', _lazy('Asia, Africa & Australia'))
)

# Untranslated as they're only seen in the admin interface.
AWARD_TYPE_CHOICES = (
    ('grand_winner', 'Grand Prize Winner'),
    ('category_winner', 'Category Winner'),
    ('runner_up', 'Runner Up'),
    ('panavision', 'Panavision Prize'),
    ('bavc', 'Bay Area Video Coalition')
)

WINNER_CATEGORY_TEXT = {
    'thirty_spot': _lazy('30 Second Spot Winner'),
    'animation': _lazy('Animation Winner'),
    'new_technology': _lazy('New Technology Winner'),
    'psa': _lazy('PSA Winner')
}


class Video(models.Model, CachingMixin):
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
    created = models.DateTimeField(auto_now_add=True,
                                   default=datetime(2012, 2, 28))

    upload_url = models.URLField(verify_exists=False, blank=False, default='',
                                 verbose_name=_lazy(u'Video File URL'))
    shortlink = models.CharField(max_length=32, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default='unsent')

    votes = models.BigIntegerField(default=0)
    views = models.BigIntegerField(default=0)
    bitly_link_db = models.URLField(verify_exists=False, blank=True, default='',
                                    verbose_name=u'Saved sharing link (mzl.la)')

    judge_mark = models.BooleanField(default=False,
                                     verbose_name=u'Marked for judges')

    objects = CachingManager()

    def embed_html(self, width=600, height=337):
        """Return the escaped HTML code to embed this video."""
        poster = ('https://d3fenhwk93s16g.cloudfront.net/%s/poster.jpg' %
                  self.shortlink)
        html = render_to_string('videos/vidly_embed.html', {
            'shortlink': self.shortlink,
            'poster': poster,
            'width': width,
            'height': height
        })
        return jinja2.Markup(html)

    @property
    def is_winner(self):
        """Return true if this video won an award."""
        return Award.objects.filter(video=self).exists()

    def __unicode__(self):
        return '%s: %s %s' % (self.id, self.shortlink, self.title)


class Award(models.Model, CachingMixin):
    """Model for contest winners."""
    video = models.ForeignKey(Video, blank=True, null=True)
    preview = models.ImageField(blank=True, upload_to=settings.PREVIEW_PATH,
                                max_length=settings.MAX_FILEPATH_LENGTH)
    category = models.CharField(max_length=50, blank=True,
                                choices=CATEGORY_CHOICES,
                                verbose_name=_lazy(u'Category'))
    region = models.CharField(max_length=50, blank=True,
                              choices=REGION_CHOICES,
                              verbose_name=_lazy(u'Region'))
    award_type = models.CharField(max_length=50, blank=False,
                                  choices=AWARD_TYPE_CHOICES)

    objects = CachingManager()

    @property
    def award_title(self):
        if self.award_type == 'grand_winner':
            return _('%(winner)s for %(region)s') % {
                'winner': _('Grand Prize Winner'),
                'region': self.get_region_display()
            }
        elif self.award_type == 'bavc':
            return _('Bay Area Video Coalition Prize Winner')
        elif self.award_type == 'panavision':
            return _('Panavision Prize Winner')
        else:
            return _('%(winner)s for %(region)s') % {
                'winner': unicode(WINNER_CATEGORY_TEXT[self.category]),
                'region': self.get_region_display()
            }

    @property
    def video_title(self):
        if self.video is None:
            return 'Video Title'
        else:
            return self.video.title

    @property
    def video_href(self):
        if self.video is None:
            return '#'
        else:
            return self.video.details_href

    @property
    def video_preview(self):
        if not self.preview:
            return '{0}img/promo-twilight.jpg'.format(settings.MEDIA_URL)
        else:
            return self.preview.url

    @property
    def submitter_name(self):
        if self.video is None:
            return 'Submitter Name'
        else:
            return self.video.user.userprofile.full_name

    @property
    def submitter_country(self):
        if self.video is None:
            return 'Submitter Country'
        else:
            return self.video.user.userprofile.country
