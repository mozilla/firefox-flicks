from django.conf import settings


def absolutify(url):
    """Add domain and protocol to link."""
    glue = '' if url.startswith('/') else '/'
    return glue.join((settings.SITE_URL, url))
