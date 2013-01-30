from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.contrib.admin import autodiscover
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.shortcuts import render

from funfactory.monkeypatches import patch
patch()

# Autodiscover admin.py files in each app
autodiscover()


def error_page(request, template, status=None):
    """
    Render error templates, found in the root /templates directory.

    If no status parameter is explicitly passed, this function assumes
    your HTTP status code is the same as your template name (i.e. passing
    a template=404 will render 404.html with the HTTP status code 404).
    """
    return render(request, '%d.html' % template, status=(status or template))


handler404 = lambda r: error_page(r, 404)
handler500 = lambda r: error_page(r, 500)
robots_txt = lambda r: HttpResponse(
   "User-agent: *\n%s: /" % ('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
   mimetype="text/plain"
)


urlpatterns = patterns('',
    url(r'', include('flicks.base.urls')),
    url(r'video/', include('flicks.videos.urls')),
    url(r'user/', include('flicks.users.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Generate a robots.txt
    (r'^robots\.txt$', robots_txt)
)


## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^404$', handler404),
        (r'^500$', handler500),
    ) + staticfiles_urlpatterns()
