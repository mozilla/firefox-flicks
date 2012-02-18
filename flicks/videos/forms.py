from django import forms

from happyforms import Form, ModelForm
from tower import ugettext_lazy as _lazy

from flicks.videos.models import CATEGORY_CHOICES, REGION_CHOICES, Video


SEARCH_CATEGORY_CHOICES = (('all', _lazy(u'All')),) + CATEGORY_CHOICES
SEARCH_REGION_CHOICES = (('all', _lazy(u'All')),) + REGION_CHOICES
SEARCH_SORT_CHOICES = (('upload_date', _lazy(u'Upload Date')),
                       ('votes', _lazy('Votes')),
                       ('views', _lazy('Views')))


class UploadForm(ModelForm):
    """Video upload form."""
    class Meta:
        model = Video
        fields = ('title', 'upload_url', 'category', 'region', 'description')

    agreement = forms.BooleanField(label=_lazy(u'I agree to the Contest Rules,'
                                                'Vid.ly terms of service and '
                                                'give Mozilla permission to '
                                                'use my video.'),
                                   required=True)


class SearchForm(Form):
    """Form for searching for videos."""
    search = forms.CharField(label=_lazy(u'Search'), required=False)
    category = forms.ChoiceField(label=_lazy(u'Category'),
                                 choices=SEARCH_CATEGORY_CHOICES)
    region = forms.ChoiceField(label=_lazy(u'Region'),
                               choices=SEARCH_REGION_CHOICES)
    sort_by = forms.ChoiceField(label=_lazy(u'Sort by'),
                                choices=SEARCH_SORT_CHOICES)
