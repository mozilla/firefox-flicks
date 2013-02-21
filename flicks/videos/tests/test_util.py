from django.core import mail
from django.test.utils import override_settings

from mock import patch
from nose.tools import eq_, ok_
from pyquery import PyQuery as pq

from flicks.base.tests import TestCase
from flicks.users.tests import UserFactory, UserProfileFactory
from flicks.videos.tests import VideoFactory
from flicks.videos.util import (send_approval_email, send_rejection_email,
                                vimeo_embed_code)


class TestVimeoEmbedCode(TestCase):
    def test_basic(self):
        result = vimeo_embed_code('id', width=5, height=2, elem_class='cls')
        iframe = pq(result)

        eq_(iframe[0].tag, 'iframe')
        ok_(iframe.hasClass('cls'))
        ok_(iframe.attr.src.startswith('https://player.vimeo.com/video/id'))
        eq_(iframe.attr.width, '5')
        eq_(iframe.attr.height, '2')


class SendApprovalEmailTests(TestCase):
    def test_basic(self):
        user = UserProfileFactory.create(user__email='boo@example.com').user
        video = VideoFactory.create(user=user)
        send_approval_email(video)
        eq_(len(mail.outbox), 1)
        eq_(mail.outbox[0].to, ['boo@example.com'])

    @patch('flicks.videos.util.use_lang')
    @override_settings(LANGUAGE_CODE='fr')
    def test_no_profile(self, use_lang):
        """
        If the user has no profile, use the installation's default language
        code for the email locale.
        """
        user = UserFactory.create(email='bar@example.com')
        video = VideoFactory.create(user=user)
        send_approval_email(video)
        eq_(len(mail.outbox), 1)
        eq_(mail.outbox[0].to, ['bar@example.com'])
        use_lang.assert_called_with('fr')


class SendRejectionEmailTests(TestCase):
    def test_invalid_user_id(self):
        """If the given user_id is invalid, do not send mail."""
        send_rejection_email(999999999999)
        eq_(len(mail.outbox), 0)

    def test_valid_user_id(self):
        """If a valid user_id is given, send a rejection email."""
        user = UserProfileFactory.create(user__email='blah@example.com').user
        send_rejection_email(user.id)
        eq_(len(mail.outbox), 1)
        eq_(mail.outbox[0].to, ['blah@example.com'])
