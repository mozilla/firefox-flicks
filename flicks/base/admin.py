from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry, DELETION
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.html import escape

from caching.base import CachingQuerySet


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base class to use for ModalAdmins across the site.

    Handles a few common tasks, like forcing CachingQuerySets to not cache
    their results in the admin interface.
    """
    def queryset(self, request):
        """Force CachingQuerySet to not cache in the admin interface."""
        qs = super(BaseModelAdmin, self).queryset(request)
        if isinstance(qs, CachingQuerySet):
            qs = qs.no_cache()
        return qs

    def message_user_error(self, request, msg):
        messages.error(request, msg)


class LogEntryAdmin(admin.ModelAdmin):
    """
    Allows review of admin actions.

    Taken from http://djangosnippets.org/snippets/2484/
    """
    date_hierarchy = 'action_time'
    readonly_fields = LogEntry._meta.get_all_field_names()
    list_filter = ('user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'change_message')
    list_display = ('__unicode__', 'action_time', 'user', 'content_type',
                    'object_link', 'action_flag', 'change_message')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            try:
                link = u'<a href="%s">%s</a>' % (
                    reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                            args=[obj.object_id]),
                    escape(obj.object_repr))
            except NoReverseMatch:
                link = escape(obj.object_repr)
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'
admin.site.register(LogEntry, LogEntryAdmin)
