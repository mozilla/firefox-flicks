from django.shortcuts import render

from session_csrf import anonymous_csrf


@anonymous_csrf
def home(request):
    """Landing page for Flicks."""
    return render(request, 'home.html')
