from django.conf.urls.defaults import patterns, url

from flicks.base import views

urlpatterns = patterns('',
    url(r'^creative$', views.creative, name='flicks.base.creative'),
    url(r'^faq$', views.faq, name='flicks.base.faq'),
    url(r'^judges$', views.judges, name='flicks.base.judges'),
    url(r'^partners$', views.partners, name='flicks.base.partners'),
    url(r'^prizes$', views.prizes, name='flicks.base.prizes'),
    url(r'^rules$', views.rules, name='flicks.base.rules'),
)
