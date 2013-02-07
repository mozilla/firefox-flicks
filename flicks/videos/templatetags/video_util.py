from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name='embed_html')
def embed_html(video):
    return mark_safe(video.embed_html())
