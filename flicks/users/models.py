from django.contrib.auth.models import User
from django.db import models

from caching.base import CachingManager, CachingMixin

from flicks.base import regions
from flicks.base.models import CountryField, LocaleField


# User class extensions
def user_unicode(self):
    """Change user string representation to use the user's email address."""
    return self.email
User.add_to_class('__unicode__', user_unicode)


@property
def user_profile(self):
    """Return this user's UserProfile, or None if one doesn't exist."""
    try:
        return self.userprofile
    except UserProfile.DoesNotExist:
        return None
User.add_to_class('profile', user_profile)


class UserProfile(models.Model, CachingMixin):
    """Additional fields required for a user."""
    user = models.OneToOneField(User, primary_key=True)
    locale = LocaleField(blank=False, default='en-us')

    # Profile info
    full_name = models.CharField(max_length=255, blank=False)
    nickname = models.CharField(max_length=255, blank=True)
    country = CountryField(blank=False)

    # Mailing address
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    mailing_country = CountryField(blank=True)
    state = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)

    objects = CachingManager()

    @property
    def display_name(self):
        return self.nickname or self.full_name

    @property
    def region(self):
        return regions.get_region(self.country)
