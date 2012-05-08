from django.core.urlresolvers import reverse
from django.shortcuts import render

from flicks.base.util import absolutify
from flicks.videos.models import Award


def winners(request):
    awards = Award.objects.filter(award_type__in=['grand_winner',
                                                   'category_winner',
                                                   'runner_up'])
    d = dict([('{0}_{1}_{2}'.format(a.award_type, a.category, a.region), a)
              for a in awards if a.award_type not in ['panavision', 'bavc']])
    d['panavision'] = Award.objects.get(award_type='panavision')
    d['bavc'] = Award.objects.get(award_type='bavc')

    return render(request, 'winners.html', d)


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
    return render(request, 'faq.html')


def rules(request):
    """Contest Rules page."""
    return render(request, 'rules.html')
