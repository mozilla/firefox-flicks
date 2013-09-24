from django.contrib import admin, auth
from django.db import models

from flicks.base.admin import NumVotesFilter
from flicks.users.models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    fieldsets = (
        (None, {'fields': ('full_name', 'nickname', 'country')}),
        ('Address', {'fields': ('address1', 'address2', 'city', 'state', 'postal_code',
                                'mailing_country')}),
    )


class UserAdmin(auth.admin.UserAdmin):
    """Configuration for the user admin pages."""
    list_display = ['email', 'nickname', 'num_votes', 'username', 'full_name', 'country',
                    'is_staff']
    search_fields = ['email', 'userprofile__nickname', 'username',
                     'userprofile__full_name', 'userprofile__nickname']
    list_filter = [NumVotesFilter, 'is_staff']
    inlines = [UserProfileInline]

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


admin.site.unregister(auth.models.User)
admin.site.register(auth.models.User, UserAdmin)
