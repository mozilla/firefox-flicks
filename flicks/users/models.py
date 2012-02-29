from django.contrib.auth.models import User
from django.db import models

from tower import ugettext_lazy as _lazy


class UserProfile(models.Model):
    """Additional fields required for a user."""
    user = models.OneToOneField(User, primary_key=True)

    country = models.CharField(max_length=100, blank=True,
                               verbose_name=_lazy(u'Country'))

    # L10n: Bio refers to a short paragraph describing a user.
    bio = models.TextField(blank=True, verbose_name=_lazy(u'Bio'))
    full_name = models.CharField(max_length=100, blank=False,
                                 verbose_name=_lazy(u'Full name'))

    # L10n: Website is used as a field name for a user's website URL
    website = models.URLField(blank=True, verbose_name=_lazy(u'Website'))
    address = models.CharField(max_length=200, blank=True,
                               verbose_name=_lazy(u'Address'))
    city = models.CharField(max_length=100, blank=True,
                            verbose_name=_lazy(u'City'))
    postal_code = models.CharField(max_length=50, blank=True,
                                   verbose_name=_lazy(u'Postal code'))
