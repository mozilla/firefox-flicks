from django.conf.urls.defaults import patterns, url

from flicks.base import views
from flicks.base.util import redirect


def redirect_to(name):
    return lambda request: redirect(name)


urlpatterns = patterns('',
    url(r'^/?$', views.home, name='flicks.base.home'),
    url(r'^faq/?$', views.faq, name='flicks.base.faq'),
    url(r'^rules/?$', views.rules, name='flicks.base.rules'),
    url(r'^judges/?$', views.judges, name='flicks.base.judges'),
    url(r'^strings/?$', views.strings, name='flicks.base.strings'),

    # Temporarily redirect all invalid locales to the home page.
    url(r'^(?:\w{2,3}(?:-\w{2}(?:-mac)?)?)?/',
        redirect_to('flicks.base.home')),
)
