from django.contrib.auth.models import User
from django.db import models


class Video(models.Model):
    """Users can only have one video associated with
    their account.
    """
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    user = models.ForeignKey(User, unique=True, blank=False)
    category = models.CharField(max_length=50, blank=False, default='')
    region = models.CharField(max_length=50, blank=False, default='')
