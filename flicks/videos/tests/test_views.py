from urllib import urlencode

from funfactory.urlresolvers import reverse
from mock import patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCase
from flicks.base.tests.tools import redirects_
from flicks.users.tests import UserProfileFactory
from flicks.videos.models import Video
from flicks.videos.tests import VideoFactory


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

    def test_post_invalid_form(self):
        """If the POSTed form is invalid, redisplay the page."""
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


class VideoListTests(TestCase):
    def setUp(self):
        super(VideoListTests, self).setUp()
        self.us_user = UserProfileFactory.create(country='us').user
        self.fr_user = UserProfileFactory.create(country='fr').user

        self.v1 = VideoFactory.create(user=self.us_user, approved=True)
        self.v2 = VideoFactory.create(user=self.fr_user, approved=True)

    def _video_list(self, **kwargs):
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

        response = self._video_list(region=1)
        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 not in videos)
        get_countries.assert_called_with('1')

    @patch('flicks.videos.views.regions.get_countries')
    def test_region_invalid(self, get_countries):
        """If region is invalid or empty, do not filter the returned videos."""
        # Region empty.
        get_countries.return_value = ['us', 'pt']
        response = self._video_list()

        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 in videos)
        ok_(not get_countries.called)

        # Region invalid.
        get_countries.return_value = None
        response = self._video_list(region='asdf')

        videos = response.context['videos']
        ok_(self.v1 in videos)
        ok_(self.v2 in videos)
        get_countries.assert_called_with('asdf')

    def test_invalid_page(self):
        """
        Invalid or missing page numbers default to the first page. Pages beyond
        the last page go to the last page.
        """
        response = self._video_list(page='asdf')
        eq_(response.context['videos'].number, 1)

        response = self._video_list(page=-1)
        eq_(response.context['videos'].number, 1)

        # Create more videos to get past 12
        for _ in range(12):
            VideoFactory.create(user=self.us_user, approved=True)

        # Pages beyond the max go to the last page
        response = self._video_list(page=5555)
        eq_(response.context['videos'].number, 2)

    def test_valid_page(self):
        # Create more videos to get past 12
        for _ in range(12):
            VideoFactory.create(user=self.us_user, approved=True)

        response = self._video_list(page=2)
        eq_(response.context['videos'].number, 2)
