from mock import patch
from nose.tools import eq_

from flicks.base.tests import TestCase
from flicks.users.tests import UserProfileFactory
from flicks.videos.search import search_videos
from flicks.videos.tests import VideoFactory


class SearchVideosTests(TestCase):
    def test_no_parameters(self):
        """
        If no parameters are passed, return a queryset of all approved videos.
        """
        VideoFactory.create(approved=False)
        v1 = VideoFactory.create(approved=True)
        v2 = VideoFactory.create(approved=True)
        eq_(list(search_videos()), [v1, v2])

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

        eq_(list(search_videos(query='does')), [v1, v2, v3])

        # ANY term in the query can be used for matching.
        eq_(list(search_videos(query='what does bylaw')), [v1, v2, v3])

        # Search is case-insensitive.
        eq_(list(search_videos(query='DoEs')), [v1, v2, v3])

        # Terms may match only part of a word in the video.
        eq_(list(search_videos(query='floor do')), [v1, v2, v3])

        # Terms only have to match on of the three possible fields.
        eq_(list(search_videos(query='mytitle')), [v1])
        eq_(list(search_videos(query='mydesc')), [v2])
        eq_(list(search_videos(query='name')), [v3])

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

        eq_(list(search_videos(region=1)), [video_fr])
        get_countries.assert_called_with(1)

    @patch('flicks.videos.views.regions.get_countries')
    def test_invaid_region(self, get_countries):
        """If the given region is invalid, do not filter by it."""
        get_countries.return_value = None
        user_fr = UserProfileFactory.create(country='fr').user
        user_pt = UserProfileFactory.create(country='pt').user

        video_fr = VideoFactory.create(user=user_fr, approved=True)
        video_pt = VideoFactory.create(user=user_pt, approved=True)

        eq_(list(search_videos(region=1)), [video_fr, video_pt])
        get_countries.assert_called_with(1)

    def test_title_sort(self):
        """By default, sort videos alphabetically by their title."""
        video_1 = VideoFactory.create(title='A', approved=True)
        video_2 = VideoFactory.create(title='C', approved=True)
        video_3 = VideoFactory.create(title='B', approved=True)

        eq_(list(search_videos()), [video_1, video_3, video_2])

    def test_popular_sort(self):
        """If sort is 'popular', sort by the number of votes."""
        video_1 = VideoFactory.create(title='A', approved=True, vote_count=4)
        video_2 = VideoFactory.create(title='C', approved=True)
        video_3 = VideoFactory.create(title='B', approved=True, vote_count=7)

        eq_(list(search_videos(sort='popular')), [video_3, video_1, video_2])
