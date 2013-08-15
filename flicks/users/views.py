from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import get_language

import django_browserid.views
import waffle

from flicks.base import regions
from flicks.base.util import redirect
from flicks.users.forms import UserProfileForm
from flicks.users.tasks import newsletter_subscribe
from flicks.videos.models import Video, Vote


@login_required
def profile(request):
    """Display and process the profile creation form."""
    form = UserProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        profile.locale = get_language()
        profile.save()

        if form.cleaned_data['mailing_list_signup']:
            format = form.cleaned_data['mailing_list_format']
            newsletter_subscribe.delay(request.user.email,
                                       source_url=request.build_absolute_uri(),
                                       format=format)

        return redirect('flicks.videos.upload')

    return render(request, 'users/profile.html', {
        'form': form,
        'regions': regions,
    })


class Verify(django_browserid.views.Verify):
    def login_success(self, *args, **kwargs):
        """
        Extend successful login to check if the user was attempting to vote for
        a video, and create the vote if they were.
        """
        response = super(Verify, self).login_success(*args, **kwargs)
        if not waffle.flag_is_active(self.request, 'r3'):
            return response

        try:
            video_id = self.request.session['vote_video']
            video = Video.objects.get(id=video_id)
            Vote.objects.get_or_create(user=self.request.user, video=video)
            del self.request.session['vote_video']

            # Set cookie so the JavaScript knows they successfully voted.
            response.set_cookie('just_voted', '1', max_age=3600, httponly=False)
        except (Video.DoesNotExist, ValueError):
            # Avoid retrying on an invalid video.
            del self.request.session['vote_video']
        except KeyError:
            pass  # Do nothing if the key never existed.

        return response

    def login_failure(self, *args, **kwargs):
        """
        Extend login failure so that if login fails, the user's attempts to
        vote for a video are cancelled.
        """
        try:
            del self.request.session['vote_video']
        except KeyError:
            pass

        return super(Verify, self).login_failure(*args, **kwargs)
