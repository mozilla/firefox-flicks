from django.contrib.auth import admin
from django.contrib.auth.models import User

from funfactory.admin import site


class UserAdmin(admin.UserAdmin):
    """Configuration for the user admin pages."""
    list_display = ['email', 'full_name', 'country', 'is_staff']
    search_fields = ['email', 'userprofile__full_name', 'bio']

    def full_name(self, user):
        return user.userprofile.full_name

    def country(self, user):
        return user.userprofile.country
site.register(User, UserAdmin)
