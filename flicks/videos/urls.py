from django.conf.urls.defaults import patterns, url

from flicks.videos import views

urlpatterns = patterns('',
    url(r'^video/(?P<video_id>\d+)$', views.details,
        name='flicks.videos.details'),
    url(r'^add_view/?$', views.ajax_add_view,
        name='flicks.videos.add_view'),
    url(r'^recent/?', views.recent, name='flicks.videos.recent'),
    url(r'^upload/?$', views.upload, name='flicks.videos.upload'),
    url(r'^notify/([\w]+)$', views.notify, name='flicks.videos.notify'),
    url(r'^upvote/(?P<video_shortlink>[\w]+)$', views.upvote,
        name='flicks.videos.upvote'),
    url(r'^video/noir/$', views.promo_video_noir,
        name='flicks.videos.promo_video_noir'),
    url(r'^video/dance/$', views.promo_video_dance,
        name='flicks.videos.promo_video_dance'),
    url(r'^video/twilight/$', views.promo_video_twilight,
        name='flicks.videos.promo_video_twilight'),
)
