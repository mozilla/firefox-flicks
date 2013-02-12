from django.shortcuts import render
from django.template import TemplateDoesNotExist
from jinja2 import TemplateNotFound


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

LINK_CCLICENSE = {
    'en-US': 'http://creativecommons.org/licenses/by-nc-sa/2.5/',
    'de': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.de',
    'fr': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.fr',
    'es': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.es',
    'nl': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.nl',
    'pl': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.pl',
    'pt-BR': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.pt_BR',
    'sl': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.sl',
    'sq': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.sq',
    'zh-CN': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.zh_CN',
    'zh-TW': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.zh_TW',
}

VIDEO_IC = {
    'en-US': '59415650',
    'de': '59416761',
    'es': '59418049',
    'fr': '59419952',
    'pt-BR': '59421007',
} 

def home(request):
    """Home page."""
    return render(request, 'home.html', {
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US']),
        'video_ic': VIDEO_IC.get(request.locale, VIDEO_IC['en-US']),
    })


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html', {
        'link_pdwiki': LINK_PDWIKI.get(request.locale, LINK_PDWIKI['en-US']),
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US']),
        'link_cclicense': LINK_CCLICENSE.get(request.locale, LINK_CCLICENSE['en-US'])
    })


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
