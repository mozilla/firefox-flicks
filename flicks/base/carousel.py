from collections import namedtuple
from datetime import datetime


ScheduleItem = namedtuple('ScheduleItem', ['start', 'end', 'slides'])
slide_schedule = (
    # EX: ScheduleItem(datetime(2013, 4, 5), datetime(2013, 4, 22), ['slide-two.html', 'slide-three.html']),
    ScheduleItem(datetime(2013, 4, 9), datetime(2013, 4, 21), ['blogpost_judges.html', 'blogpost_makeyourflickawinner.html', 'blogpost_getcreative.html']),
    ScheduleItem(datetime(2013, 4, 22), datetime(2013, 4, 30), ['blogpost_baficiwinner.html', 'blogpost_schwartzberg.html', 'blogpost_makeyourflickawinner.html']),
)


def get_slides(display_datetime=None):
    """
    Generate a list of the template paths to the slides that should be displayed
    on the homepage based on the given datetime.

    :param display_datetime:
        Datetime to use to determine which promos to display. Defaults to
        datetime.now().
    """
    display_datetime = display_datetime or datetime.now()
    return ('carousel/{0}'.format(name) for name in
            _get_slide_names(display_datetime))


def _get_slide_names(display_datetime):
    for item in slide_schedule:
        if item.start <= display_datetime <= item.end:
            return item.slides
    return ['slide-two.html', 'slide-three.html']  # Default
