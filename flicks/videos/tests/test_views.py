import socket

from django.conf import settings
from django.core import mail
from django.utils.unittest import skip

from funfactory.urlresolvers import reverse
from mock import patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCache, TestCase
from flicks.videos.forms import UploadForm
from flicks.videos.models import Video
from flicks.videos.tasks import send_video_to_vidly
from flicks.videos.tests import build_video
from flicks.videos.util import cached_viewcount


@skip
@patch.object(send_video_to_vidly, 'delay')
class UploadTests(TestCase):
    @patch.object(UploadForm, 'clean_upload_url')
    def _post(self, clean_upload_url, **kwargs):
        clean_upload_url.return_value = kwargs.get('url', 'http://test.com')
        """Execute upload view with kwargs as POST arguments."""
        args = {'title': 'Test', 'upload_url': 'http://test.com',
                'category': 'thirty_spot', 'region': 'america',
                'agreement': 'on'}
        args.update(kwargs)
        with self.activate('en-US'):
            response = self.client.post(reverse('flicks.videos.upload'), args)

        return response

    def setUp(self):
        self.user = self.build_user(login=True)

    def test_get(self, send_video_to_vidly):
        """An empty form should do nothing."""
        with self.activate('en-US'):
            self.client.get(reverse('flicks.videos.upload'))
        eq_(send_video_to_vidly.called, False)

    def test_invalid_post(self, send_video_to_vidly):
        """Invalid parameters should not create a video."""
        self._post(title='')
        eq_(send_video_to_vidly.called, False)

    def test_valid_post(self, send_video_to_vidly):
        """Valid parameters should send a video to vidly."""
        self._post()
        eq_(send_video_to_vidly.called, True)

        video = send_video_to_vidly.call_args[0][0]
        eq_(video.user, self.user)

    def test_socket_timeout(self, send_video_to_vidly):
        """A socket timeout is silent to the user."""
        send_video_to_vidly.side_effect = socket.timeout
        response = self._post()

        eq_(response.status_code, 200)
        ok_('videos/upload_complete.html' in
            [t.name for t in response.templates])


@skip
@patch.object(settings, 'VIDLY_USER_ID', '1111')
class NotifyTests(TestCase):
    def _post(self, xml, key=settings.NOTIFY_KEY):
        """Execute notify view with mock vid.ly XML."""
        with self.activate('en-US'):
            url = reverse('flicks.videos.notify', args=[key])
            response = self.client.post(url, {'xml': xml})
        return response

    def setUp(self):
        self.user = self.build_user()

    @patch.object(settings, 'NOTIFY_KEY', 'asdf')
    def test_invalid_key_forbidden(self):
        """If an invalid key is provided in the URL, return a 403 and do not
        modify the video.
        """
        xml = """<?xml version="1.0"?>
        <Response><Result><Task>
          <MediaShortLink>%(shortlink)s</MediaShortLink>
          <Status>Finished</Status>
        </Task></Result></Response>
        """

        with build_video(self.user, state='pending') as video:
            response = self._post(xml % {'shortlink': video.shortlink},
                                  'invalid_key')
            video = Video.objects.get(pk=video.pk)  # Refresh
            eq_(response.status_code, 403)
            eq_(video.state, 'pending')

    def test_valid_notification(self):
        """A valid notification updates a video's state."""
        xml = """<?xml version="1.0"?>
        <Response><Result><Task>
          <MediaShortLink>%(shortlink)s</MediaShortLink>
          <Status>Finished</Status>
        </Task></Result></Response>
        """

        with build_video(self.user, state='pending') as video:
            self._post(xml % {'shortlink': video.shortlink})
            video = Video.objects.get(pk=video.pk)  # Refresh
            eq_(video.state, 'complete')

            # Check for sent notification email
            eq_(len(mail.outbox), 1)
            with self.activate('en-US'):
                video_url = reverse('flicks.videos.details',
                                    kwargs={'video_id': video.id})
            ok_(video_url in mail.outbox[0].body)
            eq_(mail.outbox[0].to, [self.user.email])

    def test_error_notification(self):
        """An error notification updates the video's state."""
        xml = """<?xml version="1.0"?>
        <Response><Errors><Error>
          <ErrorCode>4.1</ErrorCode>
          <ErrorName>Wrong!</ErrorName>
          <Description>Desc</Description>
          <MediaShortLink>%(shortlink)s</MediaShortLink>
        </Error></Errors></Response>"""

        with build_video(self.user, state='pending') as video:
            self._post(xml % {'shortlink': video.shortlink})
            video = Video.objects.get(pk=video.pk)  # Refresh
            eq_(video.state, 'error')

            # Check for sent notification email
            eq_(len(mail.outbox), 1)
            ok_('error' in mail.outbox[0].body)
            eq_(mail.outbox[0].to, [self.user.email])


@skip
class AjaxAddViewTests(TestCase):
    def _post(self, video_id=None):
        params = {'video_id': video_id} if video_id is not None else {}
        with self.activate('en-US'):
            response = self.client.post(reverse('flicks.videos.add_view'),
                                        params)
        return response

    def test_no_video_id(self):
        """If no video_id is given, return a 404."""
        response = self._post(None)
        eq_(response.status_code, 404)

    def test_invalid_video_id(self):
        """If video_id isn't an integer, return a 404."""
        response = self._post('asdf')
        eq_(response.status_code, 404)

        # Test with control characters (bug 737564)
        # Test cache will only raise a warning on this.
        response = self._post(u"51 OR X='ss")
        eq_(response.status_code, 404)

    def test_no_video(self):
        """If there is no video with the given ID, return a 404."""
        response = self._post(9999999)
        eq_(response.status_code, 404)

    @patch('flicks.videos.util.cache', TestCache())
    def test_add_view(self):
        """If a video with the given ID exists, increment it's view count."""
        with build_video(self.build_user(), views=10) as video:
            eq_(cached_viewcount(video.id), 10)
            response = self._post(video.id)
            eq_(response.status_code, 200)
            eq_(cached_viewcount(video.id), 11)


@skip
class DetailsTests(TestCase):
    def _post(self, video, **kwargs):
        with self.activate('en-US'):
            url = reverse('flicks.videos.details',
                          kwargs={'video_id': video.id})
            response = self.client.post(url, kwargs)
        return response

    def setUp(self):
        self.user = self.build_user()

    def test_staff_mark(self):
        """Test that staff members can mark videos for later judging."""
        with build_video(self.user, judge_mark=False) as video:
            # Log in as staff user
            self.build_user(salt='staff', login=True, is_staff=True)

            eq_(Video.objects.get(pk=video.pk).judge_mark, False)
            self._post(video, admin_mark='asdf')
            eq_(Video.objects.get(pk=video.pk).judge_mark, True)

    def test_nonstaff_no_mark(self):
        """Test that normal users cannot mark videos for later judging."""
        with build_video(self.user, judge_mark=False) as video:
            # Log in as normal user
            self.build_user(salt='staff', login=True, is_staff=False)

            eq_(Video.objects.get(pk=video.pk).judge_mark, False)
            self._post(video, admin_mark='asdf')
            eq_(Video.objects.get(pk=video.pk).judge_mark, False)
