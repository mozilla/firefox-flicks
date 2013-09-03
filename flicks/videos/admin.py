from django.contrib import admin
from django.db.models import Count

from flicks.base.admin import BaseModelAdmin, NumVotesFilter
from flicks.videos import models
from flicks.videos.tasks import process_video


class SelectRelatedFieldListFilter(admin.filters.RelatedFieldListFilter):
    template = 'admin/filters_select.html'


class Video2013Admin(BaseModelAdmin):
    list_display = ['title', 'user_full_name', 'user_email', 'num_votes', 'created',
                    'vimeo_id', 'filename', 'processed', 'approved']
    list_filter = ['processed', 'approved', NumVotesFilter]

    search_fields = ['title', 'description', 'user__userprofile__full_name',
                     'user__email']
    readonly_fields = ['filename', 'processed', 'user_notified', 'created']

    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'created', 'vimeo_id', 'filename',
                       'description', 'thumbnail')
        }),
        ('Moderation', {
            'fields': ('processed', 'approved')
        })
    )

    actions = ['process_videos', 'download_thumbnails']
    change_form_template = 'admin/video2013_change_form.html'

    def queryset(self, request):
        """Add num_votes field to queryset."""
        qs = super(Video2013Admin, self).queryset(request)
        qs = qs.annotate(num_votes=Count('voters'))
        return qs

    def num_votes(self, video):
        # Use method on admin so we can sort by this field.
        return video.vote_count
    num_votes.admin_order_field = 'num_votes'

    def user_full_name(self, instance):
        return instance.user.profile.full_name if instance.user.profile else ''

    def user_email(self, instance):
        return instance.user.email

    def process_videos(self, request, queryset):
        """Synchronously run the video processing task on the selected videos."""
        for video in queryset:
            process_video(video.id)

        msg = '{0} videos processed successfully.'
        self.message_user(request, msg.format(len(queryset)))
    process_videos.short_description = 'Manually run video processing'

    def download_thumbnails(self, request, queryset):
        """Attempt to download thumbnails for the selected videos."""
        errors = []
        for video in queryset:
            try:
                video.download_thumbnail()
            except Exception, e:
                msg = 'Error downloading thumbnail for "{0}": {1}'
                errors.append(msg.format(video, e))

        # Notify user of results.
        count = len(queryset) - len(errors)
        if count > 0:
            msg = '{0} videos updated successfully.'
            self.message_user(request, msg.format(count))

        for error in errors:
            self.message_user_error(request, error)
    download_thumbnails.short_description = 'Download thumbnails from Vimeo'


class VoteAdmin(BaseModelAdmin):
    list_display = ['user_nickname', 'user_email', 'video', 'created']
    list_filter = ['created', ('video', SelectRelatedFieldListFilter)]
    search_fields = ['user__userprofile__full_name', 'user__userprofile__nickname', 'user__email',
                     'video__title']

    def user_nickname(self, vote):
        return vote.user.userprofile.nickname

    def user_email(self, vote):
        return vote.user.email


class Video2012Admin(BaseModelAdmin):
    """Configuration for the video admin pages."""
    list_display = ['title', 'user_email', 'state', 'judge_mark', 'category',
                    'region', 'shortlink', 'created']
    list_filter = ['state', 'judge_mark', 'category', 'region']
    search_fields = ['title', 'description', 'user__email']


class AwardAdmin(BaseModelAdmin):
    """Configuration for the award admin pages."""
    list_display = ['region', 'award_type', 'category', 'video', 'preview']


admin.site.register(models.Video2013, Video2013Admin)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Video2012, Video2012Admin)
admin.site.register(models.Award, AwardAdmin)
