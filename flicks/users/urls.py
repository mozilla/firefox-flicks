from django.conf.urls.defaults import patterns, url

from flicks.users import views

urlpatterns = patterns('',
    url(r'^verify/?$', views.verify, name='flicks.users.verify'),
    url(r'^edit/?$', views.edit_profile, name='flicks.users.edit_profile'),
)
