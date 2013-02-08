from django.contrib import admin

from flicks.videos.models import Award, Video2012, Video2013


class Video2013Admin(admin.ModelAdmin):
    list_display = ['title', 'user_full_name', 'user_email', 'created',
                    'vimeo_id', 'filename', 'processed', 'approved']
    list_filter = ['processed', 'approved']
    search_fields = ['title', 'description', 'user__userprofile__full_name',
                     'user__email']
    change_form_template = 'admin/video2013_change_form.html'

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

    def user_full_name(self, instance):
        return instance.user.profile.full_name if instance.user.profile else ''

    def user_email(self, instance):
        return instance.user.email
admin.site.register(Video2013, Video2013Admin)


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
