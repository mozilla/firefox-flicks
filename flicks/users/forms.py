from django import forms

from flicks.users.models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Video upload form."""
    class Meta:
        model = UserProfile
        exclude = ('user',)
