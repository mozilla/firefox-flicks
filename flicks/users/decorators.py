from functools import partial, wraps

from django.contrib.auth.decorators import login_required

from flicks.base.util import redirect


def profile_required(func=None, login_url=None):
    """
    If the current user does not have a profile, redirect them to the profile
    creation view.
    """
    if not func:
        return partial(profile_required, login_url=login_url)

    @wraps(func)
    @login_required(login_url=login_url)
    def wrapped(request, *args, **kwargs):
        if not request.user.profile:
            return redirect('flicks.users.profile')
        return func(request, *args, **kwargs)
    return wrapped
