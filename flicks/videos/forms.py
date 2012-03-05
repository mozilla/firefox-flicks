from django import forms

import jinja2
from elasticutils import S
from funfactory.urlresolvers import reverse
from happyforms import Form, ModelForm
from tower import ugettext as _, ugettext_lazy as _lazy

from flicks.videos.models import CATEGORY_CHOICES, REGION_CHOICES, Video


SEARCH_CATEGORY_CHOICES = (('all', _lazy(u'All')),) + CATEGORY_CHOICES
SEARCH_REGION_CHOICES = (('all', _lazy(u'All')),) + REGION_CHOICES


class UploadForm(ModelForm):
    """Video upload form."""
    class Meta:
        model = Video
        fields = ('title', 'upload_url', 'category', 'region', 'description')

    agreement = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)

        self.fields['agreement'].label = jinja2.Markup(_(
            u'I agree to the <a href="{contest}" target="_blank">Contest '
            'Rules<a/>, <a href="{url}" target="_blank">Vid.ly '
            'terms of service</a> and give Mozilla permission to use my '
            'video.')).format(url='http://www.encoding.com/terms',
                              contest=reverse('flicks.base.rules'))


class SearchForm(Form):
    """Form for searching for videos."""
    search = forms.CharField(label=_lazy(u'Search'), required=False)
    category = forms.ChoiceField(label=_lazy(u'Category'),
                                 choices=SEARCH_CATEGORY_CHOICES)
    region = forms.ChoiceField(label=_lazy(u'Region'),
                               choices=SEARCH_REGION_CHOICES)

    def videos(self):
        """Return an elasticutils search object that performs a search
        matching this form's parameters.
        """
        if self.is_valid():
            s = self.cleaned_data
            videos = S(Video).order_by('-created')
            if s['search']:
                videos = videos.query(title__text=s['search'])
            if s['category'] != 'all':
                videos = videos.filter(category=s['category'])
            if s['region'] != 'all':
                videos = videos.filter(region=s['region'])
        else:
            videos = []

        return videos
