from django import forms

from happyforms import ModelForm
from tower import ugettext_lazy as _lazy

from flicks.videos.models import Video


class UploadForm(ModelForm):
    """Video upload form."""
    class Meta:
        model = Video
        fields = ('title', 'upload_url', 'category', 'region', 'description')
    
    agreement = forms.BooleanField(label=_lazy(u'I agree to the Contest Rules,' 
                                                'Vid.ly terms of service and '
                                                'give Mozilla permission to use '
                                                'my video.'), required=True)
