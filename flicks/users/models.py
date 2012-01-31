from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Additional fields required for a user."""
    user = models.OneToOneField(User, primary_key=True)

    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField()
