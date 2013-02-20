from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

import jinja2
from caching.base import CachingManager, CachingMixin
from tower import ugettext as _, ugettext_lazy as _lazy

from flicks.base.util import get_object_or_none
from flicks.videos.tasks import process_approval, process_deletion
from flicks.videos.util import vidly_embed_code, vimeo_embed_code


class Video2013(models.Model, CachingMixin):
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.now)

    vimeo_id = models.IntegerField()
    filename = models.CharField(max_length=255, blank=False)

    approved = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    user_notified = models.BooleanField(default=False)

    small_thumbnail_url = models.URLField(blank=True)
    medium_thumbnail_url = models.URLField(blank=True)
    large_thumbnail_url = models.URLField(blank=True)

    objects = CachingManager()

    @property
    def region(self):
        return self.user.userprofile.region

    def save(self, *args, **kwargs):
        """
        Prior to saving, set the video's privacy on Vimeo depending on if it is
        approved.
        """
        original = get_object_or_none(Video2013, id=self.id)
        return_value = super(Video2013, self).save(*args, **kwargs)

        # Only process approval if the value changed.
        if not original or original.approved != self.approved:
            process_approval.delay(self.id)

        return return_value

    def embed_html(self, **kwargs):
        """Return the HTML code to embed this video."""
        return jinja2.Markup(vimeo_embed_code(self.vimeo_id, **kwargs))

    def thumbnail(self, size):
        return getattr(self, '{0}_thumbnail_url'.format(size), '')

    def __unicode__(self):
        profile = self.user.profile
        name = profile.display_name if profile else self.user.email
        return '`{0}` - {1}'.format(self.title, name)


@receiver(models.signals.post_delete, sender=Video2013)
def remove_video(sender, **kwargs):
    """
    Remove the deleted video from vimeo and notify the user that it has been
    declined.
    """
    video = kwargs['instance']
    process_deletion.delay(video.vimeo_id, video.user.id)


# Assign the alias "Video" to the model for the current year's contest.
Video = Video2013


### 2012 Models ###

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


class Video2012(models.Model, CachingMixin):
    # L10n: Title refers to the title of a video.
    title = models.CharField(max_length=100, blank=False,
                             verbose_name=_lazy(u'Title'))
    description = models.TextField(blank=True,
                                   verbose_name=_lazy(u'Description'))

    user_name = models.CharField(max_length=100, blank=False,
                                 default='')
    user_email = models.EmailField(blank=True)
    user_country = models.CharField(max_length=100, blank=True)

    category = models.CharField(max_length=50, blank=False,
                                choices=CATEGORY_CHOICES,
                                verbose_name=_lazy(u'Category'))
    region = models.CharField(max_length=50, blank=False,
                              choices=REGION_CHOICES,
                              verbose_name=_lazy(u'Region'))
    created = models.DateTimeField(default=datetime.now)

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
        return vidly_embed_code(self.shortlink, width=width, height=height)

    @property
    def is_winner(self):
        """Return true if this video won an award."""
        return Award.objects.filter(video=self).exists()

    def __unicode__(self):
        return '%s: %s %s' % (self.id, self.shortlink, self.title)


class Award(models.Model, CachingMixin):
    """Model for contest winners."""
    video = models.ForeignKey(Video2012, blank=True, null=True)
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
