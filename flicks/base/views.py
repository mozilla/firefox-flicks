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
    'zh-CN': 'https://zh.wikipedia.org/wiki/%E5%85%AC%E6%9C%89%E9%A2%86%E5%9F%9F',
    'zh-TW': 'https://zh.wikipedia.org/wiki/%E5%85%AC%E6%9C%89%E9%A2%86%E5%9F%9F',
    'it': 'https://it.wikipedia.org/wiki/Pubblico_dominio',
    'lij': 'https://it.wikipedia.org/wiki/Pubblico_dominio',
    'ja': 'https://ja.wikipedia.org/wiki/%E3%83%91%E3%83%96%E3%83%AA%E3%83%83%E3%82%AF%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3',
}

LINK_BRIEF = {
    'en-US': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_en-US.pdf',
    'de': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_de.pdf',
    'es': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_es-ES.pdf',
    'nl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_nl.pdf',
    'pl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_pl.pdf',
    'sl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_sl.pdf',
    'fr': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_fr.pdf',
    'zh-TW': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_zh-TW.pdf',
    'pt-BR': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_pt-BR.pdf',
    'it': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_it.pdf',
    'lij': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_lij.pdf',
    'ja': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_ja.pdf',
}


def home(request):
    """Home page."""
    return render(request, 'home.html', {
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US'])
    })


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
        'link_pdwiki': LINK_PDWIKI.get(request.locale, LINK_PDWIKI['en-US']),
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US'])
    })


def rules(request):
    """Contest Rules page."""
    return render(request, 'rules.html')


def strings(request):
    """Strings L10N page."""
    return render(request, 'strings.html')
