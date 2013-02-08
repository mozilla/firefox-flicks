from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import get_language

from commonware.response.decorators import xframe_sameorigin
from funfactory.urlresolvers import reverse

from flicks.base import regions
from flicks.base.util import redirect
from flicks.users.forms import UserProfileForm
from flicks.users.tasks import newsletter_subscribe


@login_required
@xframe_sameorigin
def profile(request):
    """Display and process the profile creation form."""
    form = UserProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.locale = get_language()
        profile.save()

        if form.cleaned_data['mailing_list_signup']:
            newsletter_subscribe.delay(request.user.email,
                                       source_url=request.build_absolute_uri())

        return redirect('flicks.videos.upload')

    return render(request, 'users/profile.html', {
        'form': form,
        'regions': regions,
    })


@xframe_sameorigin
def persona(request):
    """Display a Persona login popup and redirect the user after login."""
    return render(request, 'users/persona.html', {
        'next': request.GET.get('next', reverse('flicks.base.home'))
    })
