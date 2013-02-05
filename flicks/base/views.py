from django.shortcuts import render


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

LINK_BRIEF = {
    'en-US': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_en-US.pdf',
    #'de': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_de.pdf',
    #'es': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_es-ES.pdf',
    #'nl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_nl.pdf',
    #'pl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_pl.pdf',
    #'sl': 'http://static.mozilla.com/firefoxflicks/pdf/Filmmakers_Creative_Brief_sl.pdf',
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
    'zh-CN': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.zh.CN',
    'zh-TW': 'http://creativecommons.org/licenses/by-nc-sa/2.5/deed.zh.TW',
}


def home(request):
    """Home page."""
    return render(request, 'home.html', {
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US'])
    })


def faq(request):
    """FAQ page."""
    return render(request, 'faq.html', {
        'link_pdwiki': LINK_PDWIKI.get(request.locale, LINK_PDWIKI['en-US']),
        'link_brief': LINK_BRIEF.get(request.locale, LINK_BRIEF['en-US']),
        'link_cclicense': LINK_CCLICENSE.get(request.locale, LINK_CCLICENSE['en-US'])
    })


def strings(request):
    """Strings L10N page."""
    return render(request, 'strings.html')
