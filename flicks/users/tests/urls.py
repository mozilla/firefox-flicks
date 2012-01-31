from django.conf.urls.defaults import include, patterns, url
from django.http import HttpResponse

from flicks.users.decorators import profile_required


@profile_required
def profile_view(request, *args, **kwargs):
    return HttpResponse('test')


urlpatterns = patterns('',
    url(r'^profile_view$', profile_view, name='profile_view'),
    url(r'', include('flicks.urls')),
)
