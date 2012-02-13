from django.contrib.auth.decorators import login_required

from flicks.base.util import redirect
from flicks.users.models import UserProfile


def profile_required(func):
    """View decorator that redirects users to the create profile page if they
    have yet to create their profile. Implies (and applies) login_required.
    """
    def decorator(request, *args, **kwargs):
        if UserProfile.objects.filter(pk=request.user.pk).exists():
            return func(request, *args, **kwargs)
        else:
            return redirect('flicks.users.edit_profile')

    return login_required(decorator)
