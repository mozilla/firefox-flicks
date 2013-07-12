from django import forms

from tower import ugettext_lazy as _lazy

from flicks.base.regions import region_names
from flicks.videos.models import Video


class VideoForm(forms.ModelForm):
    filesize = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Video
        fields = ('title', 'description', 'filename')
        widgets = {
            'title': forms.TextInput(attrs={'required': 'required'}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'filename': forms.HiddenInput
        }


class VideoSearchForm(forms.Form):
    REGION_CHOICES = [('', _lazy('All Regions'))] + region_names.items()

    query = forms.CharField(required=False)
    region = forms.TypedChoiceField(
        required=False, choices=REGION_CHOICES, coerce=int,
        empty_value=None)
    sort = forms.ChoiceField(required=False, choices=(
        ('', _lazy('by Title')),
        ('popular', _lazy('by Popularity')),
    ))
