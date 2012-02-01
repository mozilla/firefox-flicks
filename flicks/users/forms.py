from happyforms import ModelForm

from flicks.users.models import UserProfile


class UserProfileForm(ModelForm):
    """Video upload form."""
    class Meta:
        model = UserProfile
        exclude = ('user',)
