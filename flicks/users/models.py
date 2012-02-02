from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Additional fields required for a user."""
    user = models.OneToOneField(User, primary_key=True)

    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    full_name = models.CharField(max_length=100, blank=False,
                                 default='Unknown')
    website = models.URLField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=50, blank=True)
