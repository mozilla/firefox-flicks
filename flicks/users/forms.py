from django import forms

import jinja2
from happyforms import ModelForm
from tower import ugettext as _

from flicks.users.models import UserProfile


class UserProfileEditForm(ModelForm):
    """User edit form."""
    class Meta:
        model = UserProfile
        fields = ('country', 'bio', 'full_name', 'website', 'address', 'city',
                  'postal_code')


class UserProfileCreateForm(UserProfileEditForm):
    """User create form."""
    agreement = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserProfileCreateForm, self).__init__(*args, **kwargs)

        self.fields['agreement'].label = jinja2.Markup(_(
            u"I'm okay with Mozilla handling this info as you explain in your "
            "<a href='{url}' target='_blank'>privacy policy</a>.")).format(
            url='http://www.mozilla.org/en-US/privacy-policy.html')
