from functools import wraps

from celery import task


def upload_process(func):
    """Mark a view as being part of the upload process."""
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        request.upload_process = True
        return func(request, *args, **kwargs)
    return wrapped


def vimeo_task(func):
    """
    Mark a function as a celery task and automatically retry if any
    VimeoServiceErrors are raised.
    """
    @task(default_retry_delay=5 * 60)  # Retry once every 5 minutes.
    @wraps(func)
    def wrapped(*args, **kwargs):
        from flicks.videos import vimeo

        try:
            return func(*args, **kwargs)
        except vimeo.VimeoServiceError, e:
            # If Vimeo is down, retry later.
            raise wrapped.retry(exc=e)
    return wrapped
