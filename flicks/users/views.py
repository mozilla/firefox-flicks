from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from commonware.response.decorators import xframe_sameorigin
from funfactory.urlresolvers import reverse

from flicks.users.forms import UserProfileForm


@login_required
@xframe_sameorigin
def profile(request):
    """Display and process the profile creation form."""
    form = UserProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.save()
        return redirect('flicks.videos.upload')

    return render(request, 'users/profile.html', {'form': form})


@xframe_sameorigin
def persona(request):
    """Display a Persona login popup and redirect the user after login."""
    return render(request, 'users/persona.html', {
        'next': request.GET.get('next', reverse('flicks.base.home'))
    })

    
def profile_static(request):
    """Static mock template for profile creation form."""
    return render(request, 'users/profile_static.html')

