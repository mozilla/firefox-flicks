from django.conf.urls.defaults import include, patterns, url

from flicks.users import views


urlpatterns = patterns('',
    url(r'^profile/$', views.profile, name='flicks.users.profile'),
    url(r'^persona/$', views.persona, name='flicks.users.persona'),

    # django-browserid
    (r'', include('django_browserid.urls')),
)
