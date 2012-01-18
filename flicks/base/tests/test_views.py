from django.test import TestCase
from funfactory.urlresolvers import reverse

from nose.tools import eq_


class BaseTest(TestCase):
    def test_views(self):
        """Validate that pages exist."""
        r = self.client.get(reverse('flicks.base.home'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.creative'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.faq'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.judges'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.legal'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.partners'), follow=True)
        eq_(200, r.status_code)

        r = self.client.get(reverse('flicks.base.prizes'), follow=True)
        eq_(200, r.status_code)
