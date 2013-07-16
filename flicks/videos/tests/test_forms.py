from django.core.exceptions import ValidationError

from mock import patch
from nose.tools import assert_raises, eq_

from flicks.base.regions import NORTH_AMERICA
from flicks.base.tests import TestCase
from flicks.videos.forms import FIELD_FILTERS, VideoSearchForm


class VideoSearchFormTests(TestCase):
    @patch('flicks.videos.forms.search_videos')
    def test_valid_search(self, search_videos):
        form = VideoSearchForm({
            'query': 'asdf',
            'field': 'title',
            'region': NORTH_AMERICA,
            'sort': 'popular'
        })

        eq_(form.perform_search(), search_videos.return_value)
        search_videos.assert_called_with(
            query='asdf',
            fields=FIELD_FILTERS['title'],
            region=NORTH_AMERICA,
            sort='popular'
        )

    @patch('flicks.videos.forms.search_videos')
    def test_empty_field_passes_none(self, search_videos):
        """If the field isn't specified, pass None to the fields parameter."""
        form = VideoSearchForm({
            'query': 'asdf',
            'region': NORTH_AMERICA,
            'sort': 'popular'
        })

        eq_(form.perform_search(), search_videos.return_value)
        search_videos.assert_called_with(query='asdf', fields=None,
                                         region=NORTH_AMERICA, sort='popular')

    def test_invalid_form(self):
        """If the form fails validation, throw a ValidationError."""
        form = VideoSearchForm({
            'region': -5,
            'sort': 'invalid'
        })

        with assert_raises(ValidationError):
            form.perform_search()
