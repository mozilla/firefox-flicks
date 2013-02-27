from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.contrib.admin import autodiscover
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.shortcuts import render

from commonware.response.decorators import xframe_sameorigin
from funfactory.monkeypatches import patch


# Funfactory monkeypatches
patch()

# Autodiscover admin.py files in each app
autodiscover()


@xframe_sameorigin
def handler500(request):
    in_overlay = getattr(request, 'in_overlay', False)
    template = 'videos/upload_error.html' if in_overlay else '500.html'
    return render(request, template, status=500)


@xframe_sameorigin
def handler404(request):
    return render(request, '404.html', status=404)


def robots_txt(request):
    permission = 'Allow' if settings.ENGAGE_ROBOTS else 'Disallow'
    return HttpResponse('User-agent: *\n{0}: /'.format(permission),
                        mimetype='text/plain')


def temp(request):
    return HttpResponse('asdf: {0}'.format(5 / 0))


urlpatterns = patterns('',
    url(r'', include('flicks.base.urls')),
    url(r'video/', include('flicks.videos.urls')),
    url(r'user/', include('flicks.users.urls')),
    url(r'temp/', temp),

    url(r'^admin/', include(admin.site.urls)),

    # Generate a robots.txt
    (r'^robots\.txt$', robots_txt)
)


## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^404$', handler404),
        (r'^500$', handler500),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    ) + staticfiles_urlpatterns()
