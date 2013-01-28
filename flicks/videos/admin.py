from django.contrib import admin

from flicks.videos.models import Award, Video


class VideoAdmin(admin.ModelAdmin):
    """Configuration for the video admin pages."""
    list_display = ['title', 'state', 'judge_mark', 'category', 'region',
                    'shortlink', 'created']
    list_filter = ['state', 'judge_mark', 'category', 'region']
    search_fields = ['title', 'description', 'user__email']
admin.site.register(Video, VideoAdmin)


class AwardAdmin(admin.ModelAdmin):
    """Configuration for the award admin pages."""
    list_display = ['region', 'award_type', 'category', 'video', 'preview']
admin.site.register(Award, AwardAdmin)
