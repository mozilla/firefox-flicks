from datetime import datetime

from mock import patch
from nose.tools import eq_

from flicks.base.carousel import get_slides, ScheduleItem
from flicks.base.tests import TestCase


mock_schedule = (
    ScheduleItem(datetime(2013, 4, 5), datetime(2013, 4, 22), ['test1.html', 'test2.html']),
    ScheduleItem(datetime(2013, 4, 26), datetime(2013, 4, 28), ['test3.html', 'test4.html']),
    ScheduleItem(datetime(2013, 4, 29), datetime(2013, 5, 2), ['test5.html', 'test6.html']),
)


@patch('flicks.base.carousel.slide_schedule', mock_schedule)
class GetSlidesTests(TestCase):
    @patch('flicks.base.carousel.datetime')
    def test_now(self, dt):
        """
        If a date isn't passed to get_slides, it should return slides for the
        current date.
        """
        dt.now.return_value = datetime(2013, 4, 8)
        eq_(list(get_slides()), ['carousel/test1.html', 'carousel/test2.html'])

    def test_display_datetime(self):
        """
        If a date is passed to get_slides, it should return slides for that date
        instead of the current date.
        """
        eq_(list(get_slides(datetime(2013, 5, 1))),
            ['carousel/test5.html', 'carousel/test6.html'])

    def test_default(self):
        """
        If the date given to get_slides doesn't match any of the configured
        dates, it should return the default slides.
        """
        eq_(list(get_slides(datetime(2012, 2, 2))),
            ['carousel/slide-two.html', 'carousel/slide-three.html'])
