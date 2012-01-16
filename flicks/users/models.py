from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Additional fields required for a user."""
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField()
    user = models.ForeignKey(User, unique=True, blank=False)
