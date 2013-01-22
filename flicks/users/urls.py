from django.conf.urls.defaults import include, patterns


urlpatterns = patterns('',
    (r'^auth/', include('django_browserid.urls')),
)
