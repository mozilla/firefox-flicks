from django.conf.urls.defaults import patterns, url

from flicks.videos import views

urlpatterns = patterns('',
    url(r'^video/(?P<video_id>[\w]+)$', views.details, name='flicks.videos.details'),
)
