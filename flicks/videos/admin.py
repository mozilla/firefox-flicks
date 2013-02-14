from django.contrib import admin

from flicks.base.admin import BaseModelAdmin
from flicks.videos.models import Award, Video2012, Video2013
from flicks.videos.tasks import process_video


class Video2013Admin(BaseModelAdmin):
    list_display = ['title', 'user_full_name', 'user_email', 'created',
                    'vimeo_id', 'filename', 'processed', 'approved']
    list_filter = ['processed', 'approved']

    search_fields = ['title', 'description', 'user__userprofile__full_name',
                     'user__email']
    readonly_fields = ['filename', 'processed', 'user_notified', 'created']

    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'created', 'vimeo_id', 'filename',
                       'description')
        }),
        ('Moderation', {
            'fields': ('processed', 'approved')
        })
    )

    actions = ['process_videos']
    change_form_template = 'admin/video2013_change_form.html'

    def user_full_name(self, instance):
        return instance.user.profile.full_name if instance.user.profile else ''

    def user_email(self, instance):
        return instance.user.email

    def process_videos(self, request, queryset):
        """Synchronously run the video processing task on the selected videos."""
        for video in queryset:
            process_video(video.id)

        count = len(queryset)
        count_string = '1 video' if count == 1 else '{0} videos'.format(count)
        self.message_user(request,
                          '{0} processed successfully.'.format(count_string))
    process_videos.short_description = 'Manually run video processing'

admin.site.register(Video2013, Video2013Admin)


class Video2012Admin(BaseModelAdmin):
    """Configuration for the video admin pages."""
    list_display = ['title', 'user_email', 'state', 'judge_mark', 'category',
                    'region', 'shortlink', 'created']
    list_filter = ['state', 'judge_mark', 'category', 'region']
    search_fields = ['title', 'description', 'user__email']
admin.site.register(Video2012, Video2012Admin)


class AwardAdmin(BaseModelAdmin):
    """Configuration for the award admin pages."""
    list_display = ['region', 'award_type', 'category', 'video', 'preview']
admin.site.register(Award, AwardAdmin)
