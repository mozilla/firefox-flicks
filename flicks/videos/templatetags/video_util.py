from django import template


register = template.Library()


@register.filter(name='embed_html')
def embed_html(video):
    return video.embed_html()
