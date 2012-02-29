from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from django_browserid.auth import get_audience
from django_browserid.forms import BrowserIDForm

from flicks.base.util import get_object_or_none, redirect
from flicks.users.forms import UserProfileCreateForm, UserProfileEditForm
from flicks.users.models import UserProfile
from flicks.videos.forms import SearchForm
from flicks.videos.models import User, Video


def details(request, user_id=None):
    """User profile page."""
    if request.user.id == user_id:
        user = request.user
        page_type = 'profile secondary user-details'
    else:
        user = get_object_or_404(User, id=user_id)
        page_type = 'secondary user-details'

    show_pagination = False

    # Handle search and filtering
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        videos = search_form.videos().filter(user_id=user_id)
    else:
        videos = (Video.objects
                  .filter(state='complete', user__id=user_id)
                  .order_by('-id'))

    pagination_limit = getattr(settings, 'PAGINATION_LIMIT_FULL', 9)

    paginator = Paginator(videos, pagination_limit)
    page = request.GET.get('page', 1)

    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    if paginator.count > pagination_limit:
        show_pagination = True

    d = dict(videos=videos.object_list,
             video_pages= videos,
             show_pagination=show_pagination,
             page_type=page_type,
             search_form=search_form,
             user=user,
             profile=user.userprofile)

    return render(request, 'users/details.html', d)


@require_POST
def verify(request):
    """Process login."""
    form = BrowserIDForm(request.POST)
    if form.is_valid():
        assertion = form.cleaned_data['assertion']
        user = auth.authenticate(assertion=assertion,
                                 audience=get_audience(request))
        if user is not None and user.is_active:
            auth.login(request, user)

            # Redirect to edit profile page if user has no profile.
            if UserProfile.objects.filter(pk=user.pk).exists():
                return redirect(settings.LOGIN_REDIRECT)
            else:
                return redirect('flicks.users.edit_profile')

    # TODO: Determine how to convey login failure.
    return redirect(settings.LOGIN_REDIRECT_FAILURE)


@login_required
def edit_profile(request):
    """Create and/or edit a user profile."""
    profile = get_object_or_none(UserProfile, pk=request.user.pk)
    if request.method == 'POST':
        if profile:
            form = UserProfileEditForm(request.POST, instance=profile)
        else:
            form = UserProfileCreateForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('flicks.users.my_profile')
    else:
        if profile:
            form = UserProfileEditForm(instance=profile)
        else:
            form = UserProfileCreateForm(instance=profile)

    d = dict(profile=profile,
             edit_form=form,
             page_type='secondary form')

    return render(request, 'users/edit_profile.html', d)


@login_required
def my_profile(request):
    """Quick link to your profile that avoids referring by user_id."""
    return redirect('flicks.users.details', args=[request.user.pk])
