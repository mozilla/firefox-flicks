from django.contrib.admin import site
from django.contrib.auth import admin
from django.contrib.auth.models import User


class UserAdmin(admin.UserAdmin):
    """Configuration for the user admin pages."""
    list_display = ['email', 'full_name', 'country', 'is_staff']
    search_fields = ['email', 'userprofile__full_name', 'bio']

    def full_name(self, user):
        return user.profile.full_name

    def country(self, user):
        return user.profile.country
site.unregister(User)
site.register(User, UserAdmin)
