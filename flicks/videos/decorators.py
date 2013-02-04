from functools import wraps

from commonware.response.decorators import xframe_sameorigin


def in_overlay(func):
    """Mark a view as being intended for display in an iframe overlay."""
    @wraps(func)
    @xframe_sameorigin
    def wrapped(request, *args, **kwargs):
        request.in_overlay = True
        return func(request, *args, **kwargs)
    return wrapped
