from django.shortcuts import render
from django.template import TemplateDoesNotExist
from jinja2 import TemplateNotFound

from flicks.base import carousel


def home(request):
    """Home page."""
    return render(request, 'home.html', {
        'slides': carousel.get_slides()
    })


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html')


def rules(request):
    """Rules page. If template does not exist default to us."""
    try:
        return render(request, 'rules/{0}.html'.format(request.locale))
    except (TemplateNotFound, TemplateDoesNotExist):
        return render(request, 'rules/en-US.html')


def judges(request):
    """Judges page."""
    return render(request, 'judges.html', {'page_type': 'judges'})


def strings(request):
    """Strings L10N page."""
    return render(request, 'strings.html')
