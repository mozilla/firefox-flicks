from django.shortcuts import get_object_or_404, render

from commonware.response.decorators import xframe_sameorigin
from tower import ugettext_lazy as _lazy

from flicks.base.util import promo_video_shortlink
from flicks.videos.models import Video2012
from flicks.videos.util import vidly_embed_code
from flicks.users.decorators import profile_required


# 2013 Contest


@profile_required
@xframe_sameorigin
def submit(request):
    return render(request, 'videos/submit.html')


def recent(request):
    """Recent videos page."""
    return render(request, 'videos/recent.html', {'page_type': 'archive'})


# 2012 Archive


def details_2012(request, video_id=None):
    """Landing page for video details."""
    video = get_object_or_404(Video2012, pk=video_id, state='complete')
    return render(request, 'videos/2012/details.html', {'video': video})


def promo_video_noir(request):
    """Film Noir promo video."""
    d = dict(video_title=_lazy('Noir'),
             video_description=_lazy('The fox meets a damsel in distress, but '
                                     'can he help her? Get inspired for your '
                                     'Firefox Flicks entry by checking out '
                                     'our video.'),
             tweet_text=_lazy('The fox meets a damsel in distress, but can he '
                              'help her?'),
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('noir'),
                                          width='100%', height=337))
    return render(request, 'videos/2012/promo.html', d)


def promo_video_dance(request):
    """Dancing promo video."""
    d = dict(video_title=_lazy('Dance'),
             video_description=_lazy("He's got the moves, he's got ambition. "
                                     "How far can this fox's feet take him? "
                                     "Get inspired for your Firefox Flicks "
                                     "entry by checking out our video."),
             tweet_text=_lazy("He's got the moves. He's got ambition. How far "
                              "can this fox's feet take him?"),
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('dance'),
                                          width='100%', height=337))
    return render(request, 'videos/2012/promo.html', d)


def promo_video_twilight(request):
    """Twilight parody promo video."""
    desc = _lazy('A teenage girl learns the truth about the fox. Get inspired '
                 'for your Firefox Flicks entry by checking out our video.')
    d = dict(video_title=_lazy('Twilight'),
             video_description=desc,
             tweet_text=desc,
             page_type='videos',
             video_embed=vidly_embed_code(promo_video_shortlink('twilight'),
                                          width='100%', height=337))
    return render(request, 'videos/2012/promo.html', d)
