from django import forms

import jinja2
from happyforms import ModelForm
from funfactory.urlresolvers import reverse
from tower import ugettext as _

from flicks.users.models import UserProfile


class UserProfileEditForm(ModelForm):
    """User edit form."""
    class Meta:
        model = UserProfile
        fields = ('country', 'bio', 'full_name', 'website', 'address', 'city',
                  'postal_code', 'youth_contest')

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)

        self.fields['youth_contest'].label = jinja2.Markup(_(
            u'I am between 13 and 19 years of age and would like to opt into '
            'the <a href="{url}">Firefox Flicks Youth Contest</a>.')).format(
            url='%s#%s' % (reverse('flicks.base.prizes'), 'youth-contest'))


class UserProfileCreateForm(UserProfileEditForm):
    """User create form."""
    agreement = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserProfileCreateForm, self).__init__(*args, **kwargs)

        self.fields['agreement'].label = jinja2.Markup(_(
            u"I'm okay with Mozilla handling this info as you explain in your "
            "<a href='{url}' target='_blank'>privacy policy</a>.")).format(
            url='http://www.mozilla.org/en-US/privacy-policy.html')
