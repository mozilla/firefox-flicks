from django import forms

import jinja2
from happyforms import Form, ModelForm
from tower import ugettext as _, ugettext_lazy as _lazy

from flicks.users.models import UserProfile


class UserProfileEditForm(ModelForm):
    """User edit form."""
    class Meta:
        model = UserProfile
        exclude = ('user',)


class UserProfileCreateForm(UserProfileEditForm):
    """User create form."""
    agreement = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserProfileCreateForm, self).__init__(*args, **kwargs)

        self.fields['agreement'].label = jinja2.Markup(_(
            u"I'm okay with Mozilla handling this info as you explain in your "
            "<a href='{url}' target='_blank'>privacy policy</a>.")).format(
        	url='http://www.mozilla.org/en-US/privacy-policy.html')
