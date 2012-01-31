from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from django_browserid.auth import get_audience
from django_browserid.forms import BrowserIDForm

from flicks.base.util import get_object_or_none, redirect
from flicks.users.forms import UserProfileForm
from flicks.users.models import UserProfile


@require_POST
def verify(request):
    """Process login."""
    form = BrowserIDForm(request.POST)
    if form.is_valid():
        assertion = form.cleaned_data['assertion']
        user = auth.authenticate(assertion=assertion,
                                 audience=get_audience(request))
        if user is not None and user.is_active:
            auth.login(request, user)

            # Redirect to edit profile page if user has no profile.
            if UserProfile.objects.filter(pk=user.pk).exists():
                return redirect(settings.LOGIN_REDIRECT)
            else:
                return redirect('flicks.users.edit_profile')

    # TODO: Determine how to convey login failure.
    return redirect(settings.LOGIN_REDIRECT_FAILURE)


@login_required
def edit_profile(request):
    """Create and/or edit a user profile."""
    profile = get_object_or_none(UserProfile, pk=request.user.pk)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('flicks.base.home')
    else:
        form = UserProfileForm(instance=profile)

    ctx = {'profile': profile, 'edit_form': form}
    return render(request, 'users/edit_profile.html', ctx)
