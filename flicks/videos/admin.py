from django.contrib import admin

from funfactory.admin import site

from flicks.videos.models import Video


class VideoAdmin(admin.ModelAdmin):
    """Configuration for the video admin pages."""
    list_display = ['title', 'user', 'state', 'category', 'region',
                    'shortlink', 'created']
    list_filter = ['state', 'category', 'region']
    search_fields = ['title', 'description', 'user__email']
site.register(Video, VideoAdmin)
