from django.conf.urls.defaults import include, patterns, url

from flicks.users import views


urlpatterns = patterns('',
    url(r'^profile/$', views.profile, name='flicks.users.profile'),

    # django-browserid
    (r'', include('django_browserid.urls')),
)
