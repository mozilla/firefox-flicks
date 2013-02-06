from nose.tools import eq_, ok_
from pyquery import PyQuery as pq

from flicks.base.tests import TestCase
from flicks.videos.util import vimeo_embed_code


class TestVimeoEmbedCode(TestCase):
    def test_basic(self):
        result = vimeo_embed_code('id', width=5, height=2, elem_class='cls')
        iframe = pq(result)

        eq_(iframe[0].tag, 'iframe')
        ok_(iframe.hasClass('cls'))
        ok_(iframe.attr.src.startswith('https://player.vimeo.com/video/id'))
        eq_(iframe.attr.width, '5')
        eq_(iframe.attr.height, '2')
