from django.shortcuts import get_object_or_404, render

from models import Video


def details(request, video_id=None):
    """Landing page for video details."""
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'videos/details.html', {'video': video})
