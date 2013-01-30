from django import forms

from flicks.users.models import UserProfile


class UserProfileForm(forms.ModelForm):
    privacy_policy_agree = forms.BooleanField(required=True)

    class Meta:
        model = UserProfile
        fields = ('full_name', 'nickname', 'country', 'address1', 'address2',
                  'city', 'mailing_country', 'state', 'postal_code')
