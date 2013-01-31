from django.contrib import admin

from flicks.videos.models import Award, Video2012


class Video2012Admin(admin.ModelAdmin):
    """Configuration for the video admin pages."""
    list_display = ['title', 'user_email', 'state', 'judge_mark', 'category',
                    'region', 'shortlink', 'created']
    list_filter = ['state', 'judge_mark', 'category', 'region']
    search_fields = ['title', 'description', 'user__email']
admin.site.register(Video2012, Video2012Admin)


class AwardAdmin(admin.ModelAdmin):
    """Configuration for the award admin pages."""
    list_display = ['region', 'award_type', 'category', 'video', 'preview']
admin.site.register(Award, AwardAdmin)
