from django.conf import settings

import basket
from celery import task


@task(default_retry_delay=30 * 60)  # Retry once every 30 minutes.
def newsletter_subscribe(email, **kwargs):
    try:
        basket.subscribe(email, settings.BASKET_FLICKS_LIST, **kwargs)
    except basket.BasketException, e:
        raise newsletter_subscribe.retry(exc=e)
