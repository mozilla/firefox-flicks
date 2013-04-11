from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.contrib.admin import autodiscover
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.shortcuts import render

from funfactory.monkeypatches import patch


# Funfactory monkeypatches
patch()

# Autodiscover admin.py files in each app
autodiscover()


def handler500(request):
    if getattr(request, 'upload_process', False):
        return handler500_upload(request)
    return render(request, '500.html', status=500)


def handler500_upload(request):
    return render(request, 'videos/upload_error.html', status=500)


def handler404(request):
    return render(request, '404.html', status=404)


def robots_txt(request):
    permission = 'Allow' if settings.ENGAGE_ROBOTS else 'Disallow'
    return HttpResponse('User-agent: *\n{0}: /'.format(permission),
                        mimetype='text/plain')


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
        (r'^500_upload$', handler500_upload),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    ) + staticfiles_urlpatterns()
