from django.conf.urls.defaults import patterns, url

from flicks.videos import views

urlpatterns = patterns(
    '',

    # Video pages
    url(r'^$', views.gallery, name='flicks.videos.list'),
    url(r'^my_voted_videos/$', views.my_voted_videos,
        name='flicks.videos.my_voted_videos'),
    url(r'^2013/(\d+)/$', views.video_detail, name='flicks.videos.detail'),
    url(r'^winners/?$', views.winners, name='flicks.videos.winners'),

    # Search pages
    url(r'^autocomplete/$', views.autocomplete,
        name='flicks.videos.autocomplete'),

    # Upload pages
    url(r'^upload/$', views.upload, name='flicks.videos.upload'),
    url(r'^upload/complete/$', views.upload_complete,
        name='flicks.videos.upload_complete'),
    url(r'^upload/error/$', views.upload_error,
        name='flicks.videos.upload_error'),

    # Voting URLs
    url(r'^2013/(\d+)/vote/$', views.vote, name='flicks.videos.vote'),
    url(r'^2013/(\d+)/unvote/$', views.unvote, name='flicks.videos.unvote'),

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
