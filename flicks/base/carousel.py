from collections import namedtuple
from datetime import date


ScheduleItem = namedtuple('ScheduleItem', ['start', 'end', 'slides'])
slide_schedule = (
    # EX: ScheduleItem(date(2013, 4, 5), date(2013, 4, 22), ['slide-two.html', 'slide-three.html']),
    ScheduleItem(date(2013, 4, 9), date(2013, 4, 21), ['blogpost_judges.html', 'blogpost_makeyourflickawinner.html', 'blogpost_getcreative.html']),
    ScheduleItem(date(2013, 4, 22), date(2013, 4, 30), ['blogpost_baficiwinner.html', 'blogpost_schwartzberg.html', 'blogpost_makeyourflickawinner.html']),
)


def get_slides(display_date=None):
    """
    Generate a list of the template paths to the slides that should be displayed
    on the homepage based on the given date.

    :param display_date:
        Date to use to determine which promos to display. Defaults to
        date.now().
    """
    display_date = display_date or date.today()
    return ('carousel/{0}'.format(name) for name in
            _get_slide_names(display_date))


def _get_slide_names(display_date):
    for item in slide_schedule:
        if item.start <= display_date <= item.end:
            return item.slides
    return ['slide-two.html', 'slide-three.html']  # Default
