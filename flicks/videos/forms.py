from django import forms

from flicks.videos.models import Video


class VideoForm(forms.ModelForm):
    filesize = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Video
        fields = ('title', 'description', 'filename')
        widgets = {
            'title': forms.TextInput(attrs={'required': 'required'}),
            'filename': forms.HiddenInput
        }
