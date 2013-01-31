from django.conf.urls.defaults import patterns, url

from flicks.videos import views

urlpatterns = patterns('',
    url(r'^submit/$', views.submit, name='flicks.videos.submit'),

    # 2012 Archive pages
    url(r'^(?P<video_id>\d+)$', views.details_2012,
        name='flicks.videos.2012.details'),
    url(r'^noir/$', views.promo_video_noir,
        name='flicks.videos.promo_video_noir'),
    url(r'^dance/$', views.promo_video_dance,
        name='flicks.videos.promo_video_dance'),
    url(r'^twilight/$', views.promo_video_twilight,
        name='flicks.videos.promo_video_twilight'),
    url(r'^videos/recent/$', views.recent, name='flicks.videos.recent')
)
