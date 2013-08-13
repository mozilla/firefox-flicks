from django.contrib.admin import site
from django.contrib.auth import admin
from django.contrib.auth.models import User
from django.db import models

from flicks.base.admin import NumVotesFilter


class UserAdmin(admin.UserAdmin):
    """Configuration for the user admin pages."""
    list_display = ['email', 'nickname', 'num_votes', 'username', 'full_name', 'country',
                    'is_staff']
    search_fields = ['email', 'userprofile__nickname', 'username',
                     'userprofile__full_name', 'userprofile__nickname']
    list_filter = [NumVotesFilter, 'is_staff']

    def queryset(self, request):
        """Add num_votes field to queryset."""
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.annotate(num_votes=models.Count('voted_videos'))
        return qs

    def full_name(self, user):
        return user.profile.full_name

    def nickname(self, user):
        return user.profile.nickname

    def country(self, user):
        return user.profile.country

    def num_votes(self, user):
        # Use method on the admin so we can sort by this field.
        return user.vote_count
    num_votes.admin_order_field = 'num_votes'
site.unregister(User)
site.register(User, UserAdmin)
