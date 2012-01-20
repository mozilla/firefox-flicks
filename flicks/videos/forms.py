from django import forms

from flicks.videos.models import Video


class UploadForm(forms.ModelForm):
    """Video upload form."""
    class Meta:
        model = Video
        fields = ('title', 'upload_url', 'category', 'region')
