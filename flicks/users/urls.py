from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.views import logout

from flicks.users import views


urlpatterns = patterns(
    '',
    url(r'^profile/$', views.profile, name='flicks.users.profile'),

    # django-browserid
    # TODO: When django-browserid supports swapping out the verify view with a
    # different class, go back to including it's urlconf and use that instead.
    # See https://github.com/mozilla/django-browserid/pull/169 for details.
    url(r'^login/', views.Verify.as_view(), name='browserid_login'),
    url(r'^logout/', logout,
        {'next_page': getattr(settings, 'LOGOUT_REDIRECT_URL', '/')},
        name='browserid_logout')
)
