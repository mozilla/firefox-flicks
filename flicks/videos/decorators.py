from functools import wraps

from celery import task
from commonware.response.decorators import xframe_sameorigin


def in_overlay(func):
    """Mark a view as being intended for display in an iframe overlay."""
    @wraps(func)
    @xframe_sameorigin
    def wrapped(request, *args, **kwargs):
        request.in_overlay = True
        return func(request, *args, **kwargs)
    return wrapped


def vimeo_task(func):
    """
    Mark a function as a celery task and automatically retry if any
    VimeoServiceErrors are raised.
    """
    @task(default_retry_delay=30 * 60)  # Retry once every 30 minutes.
    @wraps(func)
    def wrapped(*args, **kwargs):
        from flicks.videos import vimeo

        try:
            return func(*args, **kwargs)
        except vimeo.VimeoServiceError, e:
            # If Vimeo is down, retry later.
            raise wrapped.retry(exc=e)
    return wrapped
