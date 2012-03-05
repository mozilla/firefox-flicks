import socket
from contextlib import nested
from functools import partial

from django.conf import settings
from django.core import mail

from funfactory.urlresolvers import reverse
from mock import patch
from nose.tools import eq_, ok_

from flicks.base.tests import TestCache, TestCase
from flicks.videos.models import Video
from flicks.videos.tasks import send_video_to_vidly
from flicks.videos.tests import build_video
from flicks.videos.util import cached_viewcount


@patch.object(send_video_to_vidly, 'delay')
class UploadTests(TestCase):
    def _post(self, **kwargs):
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


@patch.object(settings, 'VIDLY_USER_ID', '1111')
class NotifyTests(TestCase):
    def _post(self, shortlink, user_id=1111):
        """Execute notify view with mock vid.ly XML."""
        xml = """<?xml version="1.0"?>
        <Response><Result><Task>
          <UserID>%(user_id)s</UserID>
          <MediaShortLink>%(shortlink)s</MediaShortLink>
          <Status>Finished</Status>
        </Task></Result></Response>
        """ % {'user_id': user_id, 'shortlink': shortlink}

        with self.activate('en-US'):
            response = self.client.post(reverse('flicks.videos.notify'),
                                        {'xml': xml})
        return response

    def setUp(self):
        self.user = self.build_user()

    def test_invalid_user_id(self):
        """Returning with an invalid user id fails."""
        with build_video(self.user, state='pending') as video:
            self._post(video.shortlink, '9999')
            eq_(video.state, 'pending')

    def test_valid_notification(self):
        """A valid notification updates a video's state."""
        with build_video(self.user, state='pending') as video:
            self._post(video.shortlink)
            video = Video.objects.get(pk=video.pk)  # Refresh
            eq_(video.state, 'complete')

            # Check for sent notification email
            eq_(len(mail.outbox), 1)
            with self.activate('en-US'):
                video_url = reverse('flicks.videos.details',
                                    kwargs={'video_id': video.id})
            ok_(video_url in mail.outbox[0].body)
            eq_(mail.outbox[0].to, [self.user.email])


class UpvoteTests(TestCase):
    def setUp(self):
        self._build_video = build_video(self.build_user())
        self.video = self._build_video.__enter__()

    def tearDown(self):
        self._build_video.__exit__(None, None, None)

    def _post(self, shortlink):
        with self.activate('en-US'):
            kwargs = {'video_shortlink': shortlink}
            response = self.client.post(reverse('flicks.videos.upvote',
                                                kwargs=kwargs))
        return response

    def test_already_voted(self):
        """If the user already voted, return a 403 Forbidden."""
        self.client.cookies[self.video.shortlink] = '1'
        response = self._post(self.video.shortlink)
        eq_(response.status_code, 403)
        del self.client.cookies[self.video.shortlink]

    def test_video_doesnt_exist(self):
        """If a video with the given shortlink doesn't exist, return a
        404 Not Found.
        """
        response = self._post('nonexistant_shortlink')
        eq_(response.status_code, 404)

    @patch.object(Video, 'upvote')
    def test_socket_timeout(self, video_upvote):
        """If there is an issue connecting to celery, return a
        500 Internal Server Error.
        """
        video_upvote.side_effect = socket.timeout
        response = self._post(self.video.shortlink)
        eq_(response.status_code, 500)

    def test_successful_upvote(self):
        """If no error occurs, the video vote count should increase, a cookie
        should be set, and the server should return a 200 Ok.
        """
        votes = self.video.votes
        response = self._post(self.video.shortlink)
        eq_(response.status_code, 200)
        ok_(self.video.shortlink in self.client.cookies)

        self.video = Video.objects.get(pk=self.video.pk)
        eq_(self.video.votes, votes + 1)


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
