from django.contrib import admin

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
