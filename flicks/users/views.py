from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import get_language

from flicks.base import regions
from flicks.base.util import redirect
from flicks.users.forms import UserProfileForm
from flicks.users.tasks import newsletter_subscribe


@login_required
def profile(request):
    """Display and process the profile creation form."""
    form = UserProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.locale = get_language()
        profile.save()

        if form.cleaned_data['mailing_list_signup']:
            format = form.cleaned_data['mailing_list_format']
            newsletter_subscribe.delay(request.user.email,
                                       source_url=request.build_absolute_uri(),
                                       format=format)

        return redirect('flicks.videos.upload')

    return render(request, 'users/profile.html', {
        'form': form,
        'regions': regions,
    })
