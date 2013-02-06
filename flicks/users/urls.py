from django.conf.urls.defaults import include, patterns, url

from flicks.users import views


urlpatterns = patterns('',
    url(r'^profile/$', views.profile, name='flicks.users.profile'),
    url(r'^persona/$', views.persona, name='flicks.users.persona'),
    
    # static templates for mockup
    url(r'^profile_static/$', views.profile_static, name='flicks.users.profile_static'),

    # django-browserid
    (r'', include('django_browserid.urls')),
)
