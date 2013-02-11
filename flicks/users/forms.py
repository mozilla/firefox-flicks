from django import forms

from tower import ugettext_lazy as _lazy

from flicks.base.util import country_choices
from flicks.users.models import UserProfile


class UserProfileForm(forms.ModelForm):
    # L10n: Used in a choice field where users can choose between receiving
    # L10n: HTML-based or Text-only newsletter emails.
    NEWSLETTER_FORMATS = (('html', 'HTML'), ('text', _lazy('Text')))

    privacy_policy_agree = forms.BooleanField(required=True)
    mailing_list_signup = forms.BooleanField(required=False)
    mailing_list_format = forms.ChoiceField(required=False,
                                            choices=NEWSLETTER_FORMATS,
                                            initial='html')

    class Meta:
        model = UserProfile
        fields = ('full_name', 'nickname', 'country', 'address1', 'address2',
                  'city', 'mailing_country', 'state', 'postal_code')
        widgets = {
            'full_name': forms.TextInput(attrs={'required': 'required'}),
            'privacy_policy_agree': forms.CheckboxInput(
                attrs={'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Localize countries list
        self.fields['country'].choices = country_choices(allow_empty=False)
        self.fields['mailing_country'].choices = country_choices()
