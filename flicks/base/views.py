from django.core.urlresolvers import reverse
from django.shortcuts import render

from flicks.base.util import absolutify


LINK_PDWIKI = {
    'en-US': 'https://en.wikipedia.org/wiki/Public_domain',
    'de': 'https://de.wikipedia.org/wiki/Gemeinfreiheit',
    'fr': 'https://fr.wikipedia.org/wiki/Domaine_public_%28propri%C3%A9t%C3%A9_intellectuelle%29',
    'es': 'https://es.wikipedia.org/wiki/Dominio_p%C3%BAblico',
    'nl': 'https://nl.wikipedia.org/wiki/Publiek_domein',
    'pl': 'https://pl.wikipedia.org/wiki/Domena_publiczna',
    'pt-BR': 'https://pt.wikipedia.org/wiki/Dom%C3%ADnio_p%C3%BAblico',
    'sl': 'https://sl.wikipedia.org/wiki/Javna_last',
    'sq': 'https://sq.wikipedia.org/wiki/Domen_publik',
    'zh-CN': 'https://zh.wikipedia.org/wiki/%E5%85%AC%E6%9C%89%E9%A2%86%E5%9F%9F ',
    'zh-TW': 'https://zh.wikipedia.org/wiki/%E5%85%AC%E6%9C%89%E9%A2%86%E5%9F%9F ',
}


def home(request):
    """Home page."""
    return render(request, 'home.html')


def creative(request):
    """Creative Brief page."""
    d = dict(
        promo_dance=absolutify(reverse('flicks.videos.promo_video_dance')),
        promo_noir=absolutify(reverse('flicks.videos.promo_video_noir')),
        promo_twilight=absolutify(
            reverse('flicks.videos.promo_video_twilight')),
        page_type='secondary'
    )

    return render(request, 'creative.html', d)


def judges(request):
    """Judges page."""
    return render(request, 'judges.html', {'page_type': 'secondary'})


def prizes(request):
    """Prizes page."""
    return render(request, 'prizes.html', {'page_type': 'secondary'})


def partners(request):
    """Partners page."""
    return render(request, 'partners.html', {'page_type': 'secondary'})


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html', {
        'link_pdwiki': LINK_PDWIKI.get(request.locale, LINK_PDWIKI['en-US'])
    })


def rules(request):
    """Contest Rules page."""
    return render(request, 'rules.html')


def strings(request):
    """Strings L10N page."""
    return render(request, 'strings.html')
