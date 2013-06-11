from datetime import datetime

from django.shortcuts import render
from django.template import TemplateDoesNotExist
from jinja2 import TemplateNotFound

from flicks.base import carousel


ISO_DATE_FMT = '%Y-%m-%d'


def home(request):
    """Home page."""
    # Check to see if the user wants to view promos for a specific date.
    promo_date = request.GET.get('date', None)
    if promo_date:
        try:
            promo_date = datetime.strptime(promo_date, ISO_DATE_FMT).date()
        except ValueError:
            promo_date = None  # Failure defaults to today's date.

    return render(request, 'home.html', {
        'slides': carousel.get_slides(promo_date)
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


def partners(request):
    """Partners page."""
    return render(request, 'partners.html', {'page_type': 'partners'})


def strings(request):
    """Strings L10N page."""
    return render(request, 'strings.html')
