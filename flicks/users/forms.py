from django import forms

from flicks.base.util import country_choices
from flicks.users.models import UserProfile


class UserProfileForm(forms.ModelForm):
    privacy_policy_agree = forms.BooleanField(required=True)
    mailing_list_signup = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = ('full_name', 'nickname', 'country', 'address1', 'address2',
                  'city', 'mailing_country', 'state', 'postal_code')
        widgets = {
            'full_name': forms.TextInput(attrs={'required': 'required'})
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Localize countries list
        self.fields['country'].choices = country_choices(allow_empty=False)
        self.fields['mailing_country'].choices = country_choices()
