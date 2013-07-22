from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos.models import Video
from flicks.videos.search import autocomplete_suggestion, search_videos
from flicks.videos.tests import VideoFactory


class SearchVideosTests(TestCase):
    def test_no_parameters(self):
        """
        If no parameters are passed, return a queryset of all approved videos.
        """
        VideoFactory.create(approved=False)
        v1 = VideoFactory.create(approved=True)
        v2 = VideoFactory.create(approved=True)
        eq_(set(search_videos()), set([v1, v2]))

    def test_query(self):
        """
        If a search query is given, the results should be limited to videos
        that contain any of the terms in their title, description, or user's
        full name.
        """
        VideoFactory.create(title='no match', approved=True)
        VideoFactory.create(description='no match', approved=True)
        user = UserProfileFactory.create(full_name='no match').user
        VideoFactory.create(user=user, approved=True)

        v1 = VideoFactory.create(title='A does match mytitle', approved=True)
        v2 = VideoFactory.create(title='B', description='does match mydesc',
                                 approved=True)
        user = UserProfileFactory.create(full_name='does match name').user
        v3 = VideoFactory.create(title='C', user=user, approved=True)

        eq_(set(search_videos(query='does')), set([v1, v2, v3]))

        # ANY term in the query can be used for matching.
        eq_(set(search_videos(query='what does bylaw')), set([v1, v2, v3]))

        # Search is case-insensitive.
        eq_(set(search_videos(query='DoEs')), set([v1, v2, v3]))

        # Terms may match only part of a word in the video.
        eq_(set(search_videos(query='floor do')), set([v1, v2, v3]))

        # Terms only have to match one of the three possible fields.
        eq_(set(search_videos(query='mytitle')), set([v1]))
        eq_(set(search_videos(query='mydesc')), set([v2]))
        eq_(set(search_videos(query='name')), set([v3]))

    def test_fields(self):
        """
        If the fields parameter is specified, only perform a search on the
        fields specified in that list.
        """
        v1 = VideoFactory.create(title='foo', description='bar', approved=True)
        v2 = VideoFactory.create(title='bar', description='foo', approved=True)

        eq_(set(search_videos('foo', fields=['title'])), set([v1]))
        eq_(set(search_videos('bar', fields=['title'])), set([v2]))
        eq_(set(search_videos('bar', fields=['description'])), set([v1]))
        videos = search_videos(
            'bar', fields=['title', 'description'], sort='title')
        eq_(set(videos), set([v2, v1]))

    @patch('flicks.videos.views.regions.get_countries')
    def test_region(self, get_countries):
        """
        If the region filter is given, only return videos from countries in
        that region.
        """
        get_countries.return_value = ['us', 'fr']
        user_fr = UserProfileFactory.create(country='fr').user
        user_pt = UserProfileFactory.create(country='pt').user

        video_fr = VideoFactory.create(user=user_fr, approved=True)
        VideoFactory.create(user=user_pt, approved=True)

        eq_(set(search_videos(region=1)), set([video_fr]))
        get_countries.assert_called_with(1)

    @patch('flicks.videos.views.regions.get_countries')
    def test_invaid_region(self, get_countries):
        """If the given region is invalid, do not filter by it."""
        get_countries.return_value = None
        user_fr = UserProfileFactory.create(country='fr').user
        user_pt = UserProfileFactory.create(country='pt').user

        video_fr = VideoFactory.create(user=user_fr, approved=True)
        video_pt = VideoFactory.create(user=user_pt, approved=True)

        eq_(set(search_videos(region=1)), set([video_fr, video_pt]))
        get_countries.assert_called_with(1)

    def test_random_sort(self):
        """By default, sort the videos by their random_ordering index."""
        video_1 = VideoFactory.create(random_ordering=3, approved=True)
        video_2 = VideoFactory.create(random_ordering=1, approved=True)
        video_3 = VideoFactory.create(random_ordering=2, approved=True)

        eq_(list(search_videos()), [video_2, video_3, video_1])

    def test_title_sort(self):
        """If sort is 'title', sort videos alphabetically by their title."""
        video_1 = VideoFactory.create(title='A', approved=True)
        video_2 = VideoFactory.create(title='C', approved=True)
        video_3 = VideoFactory.create(title='B', approved=True)

        eq_(list(search_videos(sort='title')), [video_1, video_3, video_2])

    def test_popular_sort(self):
        """If sort is 'popular', sort by the number of votes."""
        video_1 = VideoFactory.create(title='A', approved=True, vote_count=4)
        video_2 = VideoFactory.create(title='C', approved=True)
        video_3 = VideoFactory.create(title='B', approved=True, vote_count=7)

        eq_(list(search_videos(sort='popular')), [video_3, video_1, video_2])


class AutocompleteSuggestionTests(TestCase):
    def setUp(self):
        self.patch = patch('flicks.videos.search.search_videos')
        self.mock_search_videos = self.patch.start()

        self.v1 = VideoFactory.create(title='foo')
        self.v2 = VideoFactory.create(title='baz')
        self.mock_search_videos.return_value = Video.objects.filter(
            id__in=[self.v1.id, self.v2.id]).order_by('id')

    def tearDown(self):
        self.patch.stop()

    def test_result_found(self):
        """
        If a video is found matching the query, return the value of the field
        we searched for on that video.
        """
        suggestion = autocomplete_suggestion('fo', 'title')
        eq_(suggestion, 'foo')  # Title of the first result.
        self.mock_search_videos.assert_called_with(query='fo',
                                                   fields=('title',))

    def test_no_results(self):
        """If no videos are matched, return None."""
        self.mock_search_videos.return_value = Video.objects.filter(id=9999999)
        eq_(autocomplete_suggestion('fo', 'title'), None)
