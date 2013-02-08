from django.conf.urls.defaults import patterns, url

from flicks.videos import views

urlpatterns = patterns('',
    # Video pages
    url(r'^$', views.video_list, name='flicks.videos.list'),
    url(r'^2013/(\d+)/$', views.video_detail, name='flicks.videos.detail'),

    # Upload pages
    url(r'^upload/$', views.upload, name='flicks.videos.upload'),
    url(r'^upload/complete/$', views.upload_complete,
        name='flicks.videos.upload_complete'),

    # 2012 Archive pages
    url(r'^(?P<video_id>\d+)$', views.details_2012,
        name='flicks.videos.2012.details'),
    url(r'^noir/$', views.promo_video_noir,
        name='flicks.videos.promo_video_noir'),
    url(r'^dance/$', views.promo_video_dance,
        name='flicks.videos.promo_video_dance'),
    url(r'^twilight/$', views.promo_video_twilight,
        name='flicks.videos.promo_video_twilight'),
)
