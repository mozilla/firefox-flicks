from django.contrib.admin import site
from django.contrib.auth import admin
from django.contrib.auth.models import User


class UserAdmin(admin.UserAdmin):
    """Configuration for the user admin pages."""
    list_display = ['email', 'nickname', 'username', 'full_name', 'country',
                    'is_staff']
    search_fields = ['email', 'userprofile__nickname', 'username',
                     'userprofile__full_name', 'userprofile__nickname']

    def full_name(self, user):
        return user.profile.full_name

    def nickname(self, user):
        return user.profile.nickname

    def country(self, user):
        return user.profile.country
site.unregister(User)
site.register(User, UserAdmin)
