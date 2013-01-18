from django.conf import settings

from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.videos.tests import build_video
from flicks.videos.models import Video


@patch('flicks.videos.models.generate_bitly_link')
class VideoBitlyLinkTests(TestCase):
    def setUp(self):
        self.user = self.build_user()
        self.long_url = 'http://test.com/video/%s'

    @patch.object(settings, 'DEV', False)
    def test_existing_link(self, generate):
        """If a link is already in the DB, don't generate a new one."""
        with build_video(self.user, bitly_link_db='asdf') as video:
            eq_(video.bitly_link, 'asdf')
            eq_(generate.called, False)

    @patch.object(settings, 'DEV', True)
    def test_no_generate_dev(self, generate):
        """If this is a dev environment, don't generate a link."""
        print 'DEV=', settings.DEV
        with build_video(self.user) as video:
            eq_(video.bitly_link, self.long_url % video.id)
            eq_(generate.called, False)

    @patch.object(settings, 'DEV', False)
    def test_fallback(self, generate):
        """If bit.ly fails, return the long URL as a fallback."""
        generate.return_value = None
        with build_video(self.user) as video:
            eq_(video.bitly_link, self.long_url % video.id)
            eq_(generate.called, True)

    @patch.object(settings, 'DEV', False)
    def test_success(self, generate):
        """If bit.ly is successful, save and return shortened link."""
        generate.return_value = 'asdf'
        with build_video(self.user) as video:
            eq_(video.bitly_link, 'asdf')
            eq_(generate.called, True)
            eq_(Video.objects.get(pk=video.pk).bitly_link_db, 'asdf')
