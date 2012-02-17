from django.conf.urls.defaults import include, patterns, url

from flicks.users import views

urlpatterns = patterns('',
    url(r'^verify/?$', views.verify, name='flicks.users.verify'),
    url(r'^edit/?$', views.edit_profile, name='flicks.users.edit_profile'),
    url(r'^details/(?P<user_id>[\w]+)$', views.details,
        name='flicks.users.details'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='flicks.users.logout'),
    url(r'^profile$', views.my_profile, name='flicks.users.my_profile'),
    url(r'^csp', include('csp.urls')),
)
