from django.core.exceptions import ValidationError
from django.test.client import RequestFactory

from mock import patch
from nose.tools import assert_raises, eq_, ok_
from waffle import Flag

from flicks.base.regions import NORTH_AMERICA
from flicks.base.tests import TestCase
from flicks.videos.forms import VideoSearchForm
from flicks.videos.search import AUTOCOMPLETE_FIELDS


class VideoSearchFormTests(TestCase):
    def setUp(self):
        super(VideoSearchFormTests, self).setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_popular_sort_include(self):
        """If the voting-end waffle flag is not set, include the popular option for sorting."""
        Flag.objects.create(name='voting-end', everyone=False)
        form = VideoSearchForm(self.request)
        ok_('popular' in [c[0] for c in form.fields['sort'].choices])

    def test_popular_sort_exclude(self):
        """If the voting-end waffle flag is set, do not include the popular option for sorting."""
        Flag.objects.create(name='voting-end', everyone=True)
        form = VideoSearchForm(self.request)
        ok_('popular' not in [c[0] for c in form.fields['sort'].choices])

    @patch('flicks.videos.forms.search_videos')
    def test_valid_search(self, search_videos):
        form = VideoSearchForm(self.request, {
            'query': 'asdf',
            'field': 'title',
            'region': NORTH_AMERICA,
            'sort': 'popular'
        })

        eq_(form.perform_search(), search_videos.return_value)
        search_videos.assert_called_with(
            query='asdf',
            fields=AUTOCOMPLETE_FIELDS['title'],
            region=NORTH_AMERICA,
            sort='popular'
        )

    @patch('flicks.videos.forms.search_videos')
    def test_empty_field_passes_none(self, search_videos):
        """If the field isn't specified, pass None to the fields parameter."""
        form = VideoSearchForm(self.request, {
            'query': 'asdf',
            'region': NORTH_AMERICA,
            'sort': 'popular'
        })

        eq_(form.perform_search(), search_videos.return_value)
        search_videos.assert_called_with(query='asdf', fields=None,
                                         region=NORTH_AMERICA, sort='popular')

    def test_invalid_form(self):
        """If the form fails validation, throw a ValidationError."""
        form = VideoSearchForm(self.request, {
            'region': -5,
            'sort': 'invalid'
        })

        with assert_raises(ValidationError):
            form.perform_search()

    def test_clean_no_query(self):
        """
        If no search query is specified, do not alter the sort value or
        choices.
        """
        form = VideoSearchForm(self.request, {'region': NORTH_AMERICA, 'sort': 'title'})
        form.full_clean()

        eq_(form.cleaned_data['sort'], 'title')
        choice_values = zip(*form.fields['sort'].choices)[0]
        ok_('' in choice_values)

    def test_clean_query(self):
        """
        If a search query is specified, remove the random option from the sort
        choices and, if the sort is currently set to random, switch to title
        sort.
        """
        form = VideoSearchForm(self.request, {'query': 'blah', 'sort': ''})
        form.full_clean()

        eq_(form.cleaned_data['sort'], 'title')
        choice_values = zip(*form.fields['sort'].choices)[0]
        ok_('' not in choice_values)

        # Check that sort is preserved if it is not random.
        form = VideoSearchForm(self.request, {'query': 'blah', 'sort': 'popular'})
        form.full_clean()

        eq_(form.cleaned_data['sort'], 'popular')
        choice_values = zip(*form.fields['sort'].choices)[0]
        ok_('' not in choice_values)

    def test_invalid_sort(self):
        """
        An invalid value for sort should not break clean.

        Regression test for an issue where a user was attempting to break Flicks by submitting a
        bunch of invalid values for sort.
        """
        form = VideoSearchForm(self.request, {'query': 'blah', 'sort': 'invalid'})
        form.full_clean()
        eq_(form.is_valid(), False)
