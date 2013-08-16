import json
from urllib import urlencode

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test.client import RequestFactory
from django.test.utils import override_settings

from funfactory.urlresolvers import reverse
from mock import Mock, patch
from nose.tools import eq_, ok_
from waffle import Flag

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.tests import UserFactory, UserProfileFactory
from flicks.videos.models import Video, Vote
from flicks.videos.tests import VideoFactory
from flicks.videos.views import video_list


class TestUpload(TestCase):
    def setUp(self):
        super(TestUpload, self).setUp()
        self.user = UserProfileFactory.create(user__email='a@b.com').user
        self.browserid_login(self.user.email)

    def _upload(self, method, ticket=None, **data):
        if ticket:
            session = self.client.session
            session['vimeo_ticket'] = ticket
            session.save()

        with self.activate('en-US'):
            url = reverse('flicks.videos.upload')
        return getattr(self.client, method)(url, data)

    @patch('flicks.videos.views.vimeo.get_new_ticket')
    def test_get_no_ticket(self, get_new_ticket):
        """
        If the user has no ticket in a GET request, retrieve one and store it in
        the session.
        """
        get_new_ticket.return_value = 'asdf'
        response = self._upload('get')

        eq_(response.client.session['vimeo_ticket'], 'asdf')
        self.assertTemplateUsed(response, 'videos/upload.html')

    @patch('flicks.videos.views.vimeo')
    def test_get_invalid_ticket(self, vimeo):
        """
        If the user has an invalid ticket in a GET request, retrieve one and
        replace the existing one in the session.
        """
        vimeo.is_ticket_valid.return_value = False
        vimeo.get_new_ticket.return_value = {'id': 'qwer'}
        response = self._upload('get', ticket={'id': 'asdf'})

        eq_(response.client.session['vimeo_ticket'], {'id': 'qwer'})
        self.assertTemplateUsed(response, 'videos/upload.html')

    @patch('flicks.videos.views.vimeo')
    def test_get_valid_ticket(self, vimeo):
        """
        If the user has a valid ticket in a GET request, do not replace the
        existing one.
        """
        vimeo.is_ticket_valid.return_value = True
        response = self._upload('get', ticket={'id': 'asdf'})

        eq_(response.client.session['vimeo_ticket'], {'id': 'asdf'})
        eq_(vimeo.get_new_ticket.called, False)
        self.assertTemplateUsed(response, 'videos/upload.html')

    @patch('flicks.videos.views.vimeo')
    def test_post_invalid_form(self, vimeo):
        """If the POSTed form is invalid, redisplay the page."""
        vimeo.is_ticket_valid.return_value = False
        vimeo.get_new_ticket.return_value = {'id': 'qwer'}
        response = self._upload('post', title=None)
        self.assertTemplateUsed(response, 'videos/upload.html')

    @patch('flicks.videos.views.vimeo')
    def test_post_verify_fail(self, vimeo):
        """If verifying uploaded data fails, display the error page."""
        vimeo.verify_chunks.return_value = False
        response = self._upload('post', ticket={'id': 'asdf'}, title='asdf',
                                filename='asdf.mp3', filesize=5)

        vimeo.verify_chunks.assert_called_with('asdf', 5)
        eq_(response.status_code, 500)
        self.assertTemplateUsed(response, 'videos/upload_error.html')

    @patch('flicks.videos.tasks.process_video')
    @patch('flicks.videos.views.vimeo')
    def test_post_success(self, vimeo, process_video):
        """
        If a valid form is POSTed and the upload checks out, create a new video,
        remove the upload ticket from the session, and return a redirect to the
        upload complete page.
        """

        vimeo.verify_chunks.return_value = True
        vimeo.complete_upload.return_value = {'video_id': '563'}
        response = self._upload('post', ticket={'id': 'asdf'}, title='qwer',
                                filename='qwer.mp4', filesize=5)

        vimeo.complete_upload.assert_called_with('asdf', 'qwer.mp4')
        videos = Video.objects.filter(title='qwer', filename='qwer.mp4',
                                      vimeo_id=563, user=self.user)
        eq_(len(videos), 1)
        process_video.delay.assert_called_with(videos[0].id)
        ok_('vimeo_id' not in response.client.session)
        redirects_(response, 'flicks.videos.upload_complete')


class GalleryTests(TestCase):
    def setUp(self):
        super(GalleryTests, self).setUp()
        self.us_user = UserProfileFactory.create(country='us').user
        self.fr_user = UserProfileFactory.create(country='fr').user

        self.v1 = VideoFactory.create(user=self.us_user, approved=True)
        self.v2 = VideoFactory.create(user=self.fr_user, approved=True)

    def _gallery(self, **kwargs):
        with self.activate('en-US'):
            url = '?'.join([reverse('flicks.videos.list'), urlencode(kwargs)])
            return self.client.get(url)

    @patch('flicks.videos.views.regions.get_countries')
    def test_region(self, get_countries):
        """
        If region is specified, filter the returned videos to only ones
        available in that region.
        """
        get_countries.return_value = ['us', 'pt']

        response = self._gallery(region=1)
        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 not in videos)
        get_countries.assert_called_with('1')

    @patch('flicks.videos.views.regions.get_countries')
    def test_region_invalid(self, get_countries):
        """If region is invalid or empty, do not filter the returned videos."""
        # Region empty.
        get_countries.return_value = ['us', 'pt']
        response = self._gallery()

        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 in videos)
        ok_(not get_countries.called)

        # Region invalid.
        get_countries.return_value = None
        response = self._gallery(region='asdf')

        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 in videos)
        get_countries.assert_called_with('asdf')

    @patch('flicks.videos.views.VideoSearchForm')
    def test_r3_video_search(self, VideoSearchForm):
        """
        If the voting flag is active, use the VideoSearchForm to determine the
        videos being paginated.
        """
        Flag.objects.create(name='voting', everyone=True)
        form = VideoSearchForm.return_value

        response = self._gallery()
        eq_(response.context['form'], form)
        eq_(response.context['videos'].paginator.object_list,
            form.perform_search.return_value)

    @patch('flicks.videos.views.VideoSearchForm')
    @patch('flicks.videos.views.search_videos')
    def test_invalid_search(self, search_videos, VideoSearchForm):
        """
        If a the search form isn't valid, perform an empty video search to
        determine the videos being paginated.
        """
        Flag.objects.create(name='voting', everyone=True)
        form = VideoSearchForm.return_value
        form.perform_search.side_effect = ValidationError('asdf')

        response = self._gallery()
        eq_(response.context['videos'].paginator.object_list,
            search_videos.return_value)


class VideoListTests(TestCase):
    def setUp(self):
        super(VideoListTests, self).setUp()
        self.factory = RequestFactory()

    def _video_list_ctx(self, ctx=None, **kwargs):
        request = self.factory.get('/', kwargs)
        with patch('flicks.videos.views.render') as render:
            video_list(request, Video.objects.all(), ctx)
            return render.call_args[0][2]

    @patch('flicks.videos.views.VideoSearchForm')
    def test_form(self, VideoSearchForm):
        """
        If the given context has a form, do not replace it. If it doesn't, add
        a VideoSearchForm to it.
        """
        form = Mock()
        ctx = self._video_list_ctx(ctx={'form': form})
        eq_(ctx['form'], form)
        ok_(not VideoSearchForm.called)

        ctx = self._video_list_ctx()
        eq_(ctx['form'], VideoSearchForm.return_value)

    @override_settings(VIDEOS_PER_PAGE=12)
    def test_invalid_page(self):
        """
        Invalid or missing page numbers default to the first page. Pages beyond
        the last page or negative pages go to the last page.
        """
        for _ in range(30):
            VideoFactory.create(approved=True)

        ctx = self._video_list_ctx(page=1)
        eq_(ctx['videos'].number, 1)

        ctx = self._video_list_ctx(page=-1)
        eq_(ctx['videos'].number, 3)

        ctx = self._video_list_ctx(page='asdf')
        eq_(ctx['videos'].number, 1)

        ctx = self._video_list_ctx()
        eq_(ctx['videos'].number, 1)

        # Pages beyond the max go to the last page
        ctx = self._video_list_ctx(page=5555)
        eq_(ctx['videos'].number, 3)

    @override_settings(VIDEOS_PER_PAGE=12)
    def test_valid_page(self):
        # Create more videos to get past 12
        for _ in range(14):
            VideoFactory.create(approved=True)

        ctx = self._video_list_ctx(page=2)
        eq_(ctx['videos'].number, 2)


@patch('flicks.videos.views.video_list')
class MyVotedVideosTests(TestCase):
    def setUp(self):
        super(MyVotedVideosTests, self).setUp()
        Flag.objects.create(name='voting', everyone=True)

    def _my_voted_videos(self, user):
        self.browserid_login(user.email)
        with self.activate('en-US'):
            return self.client.get(reverse('flicks.videos.my_voted_videos'))

    def test_basic(self, video_list):
        """
        my_voted_videos should list all the videos a user has voted for in the
        reverse order that they voted for them.
        """
        video_list.return_value = HttpResponse()

        user = UserFactory.create()
        v1 = VideoFactory.create(approved=True)
        v2 = VideoFactory.create(approved=True)
        Vote.objects.create(user=user, video=v1)
        Vote.objects.create(user=user, video=v2)
        for _ in range(14):
            VideoFactory.create(approved=True)

        response = self._my_voted_videos(user)
        eq_(response, video_list.return_value)

        videos = video_list.call_args[0][1]
        eq_(list(videos), [v2, v1])  # Also asserts the order of the votes.

    def test_empty(self, video_list):
        """
        If a user hasn't voted for any videos, my_voted_videos should be empty.
        """
        video_list.return_value = HttpResponse()

        user = UserFactory.create()
        for _ in range(14):
            VideoFactory.create(approved=True)

        response = self._my_voted_videos(user)
        eq_(response, video_list.return_value)

        videos = video_list.call_args[0][1]
        eq_(list(videos), [])


class AutocompleteTests(TestCase):
    def setUp(self):
        super(AutocompleteTests, self).setUp()
        Flag.objects.create(name='voting', everyone=True)

    def _autocomplete(self, **kwargs):
        with self.activate('en-US'):
            return self.client.get(reverse('flicks.videos.autocomplete'),
                                   kwargs)

    def test_no_query(self):
        """If no query is passed, return a 400 Bad Request."""
        response = self._autocomplete()
        eq_(response.status_code, 400)

        response = self._autocomplete(query='')
        eq_(response.status_code, 400)

        response = self._autocomplete(query='   ')
        eq_(response.status_code, 400)

    @patch('flicks.videos.views.AUTOCOMPLETE_FIELDS', {
           'title': ('title',),
           'description': ('description',)
    })
    @patch('flicks.videos.views.autocomplete_suggestion')
    def test_with_query(self, autocomplete_suggestion):
        autocomplete_suggestion.return_value = 'asdf'
        response = self._autocomplete(query='foo bar')

        eq_(response.status_code, 200)
        eq_(json.loads(response.content),
            {'by_title': 'asdf', 'by_description': 'asdf'})


class VoteAjaxTests(TestCase):
    def setUp(self):
        super(VoteAjaxTests, self).setUp()
        Flag.objects.create(name='voting', everyone=True)

    def _vote_ajax(self, video_id):
        with self.activate('en-US'):
            url = reverse('flicks.videos.vote', args=(video_id,))
        return self.client.post(url)

    def test_user_not_authenticated(self):
        """
        If the user isn't authenticated, store the video ID in their session.
        When they next log on, the vote will be saved.
        """
        response = self._vote_ajax(24)
        eq_(response.status_code, 200)
        eq_(self.client.session['vote_video'], '24')

    def test_authed_user_no_video(self):
        """If the user is authed but the video is invalid, return a 404."""
        user = UserFactory.create()
        self.browserid_login(user.email)
        response = self._vote_ajax(99999)
        eq_(response.status_code, 404)

    def test_authed_user_video_exists(self):
        """If the user is authed and the video exists, add a vote for it."""
        user = UserFactory.create()
        self.browserid_login(user.email)
        video = VideoFactory.create()

        response = self._vote_ajax(video.id)
        eq_(response.status_code, 200)
        ok_(Vote.objects.filter(user=user, video=video).exists())

        # If the vote already exists, don't add a new one.
        response = self._vote_ajax(video.id)
        eq_(response.status_code, 200)
        eq_(Vote.objects.filter(user=user, video=video).count(), 1)


class UnvoteAjaxTests(TestCase):
    def setUp(self):
        super(UnvoteAjaxTests, self).setUp()
        Flag.objects.create(name='voting', everyone=True)

    def _unvote_ajax(self, video_id):
        with self.activate('en-US'):
            url = reverse('flicks.videos.unvote', args=(video_id,))
        return self.client.post(url)

    def test_user_not_authenticated(self):
        """If the user isn't authenticated, return a 404 (no vote exists)."""
        response = self._unvote_ajax(24)
        eq_(response.status_code, 404)

    def test_no_vote(self):
        """If the user hasn't voted for the given video, return a 404."""
        user = UserFactory.create()
        self.browserid_login(user.email)
        video = VideoFactory.create()

        response = self._unvote_ajax(video.id)
        eq_(response.status_code, 404)

    def test_vote_exists(self):
        """If the user has voted for the given video, delete the vote."""
        user = UserFactory.create()
        self.browserid_login(user.email)
        video = VideoFactory.create()
        Vote.objects.create(user=user, video=video)

        response = self._unvote_ajax(video.id)
        eq_(response.status_code, 200)
        ok_(not Vote.objects.filter(user=user, video=video).exists())
