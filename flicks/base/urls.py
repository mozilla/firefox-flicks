from django.conf.urls.defaults import patterns, url

from flicks.base import views

urlpatterns = patterns('',
    url(r'^/?$', views.home, name='flicks.base.home'),
    url(r'^faq/?$', views.faq, name='flicks.base.faq'),
    url(r'^strings/?$', views.strings, name='flicks.base.strings'),
)
