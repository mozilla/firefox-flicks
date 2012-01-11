from django.http import Http404
from django.shortcuts import render


def home(request):
    """Landing page for Flicks."""
    return render(request, 'home.html')
