from django.conf.urls.defaults import patterns, url

from flicks.base import views

urlpatterns = patterns('',
    url(r'^/?$', views.home, name='flicks.base.home'),
    url(r'^faq/?$', views.faq, name='flicks.base.faq'),
    url(r'^rules/?$', views.rules, name='flicks.base.rules'),
    url(r'^judges/?$', views.judges, name='flicks.base.judges'),
    url(r'^strings/?$', views.strings, name='flicks.base.strings'),
)
