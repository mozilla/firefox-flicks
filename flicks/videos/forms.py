from django import forms

from flicks.videos.models import Video2013


class Video2013Form(forms.ModelForm):
    class Meta:
        model = Video2013
        fields = ('title', 'description', 'filename')
        widgets = {
            'filename': forms.HiddenInput
        }
