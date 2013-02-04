from django import forms

from flicks.videos.models import Video2013


class Video2013Form(forms.ModelForm):
    filesize = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Video2013
        fields = ('title', 'description', 'filename')
        widgets = {
            'title': forms.TextInput(attrs={'required': 'required'}),
            'filename': forms.HiddenInput
        }
