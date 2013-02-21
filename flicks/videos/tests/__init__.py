from factory import Factory, Sequence, SubFactory

from flicks.users.tests import UserFactory
from flicks.videos import models


class Video2013Factory(Factory):
    FACTORY_FOR = models.Video

    user = SubFactory(UserFactory)
    title = 'Test title'
    description = 'Test desc'
    vimeo_id = Sequence(lambda n: int(n))
    filename = Sequence(lambda n: '{0}.mp4'.format(n))
VideoFactory = Video2013Factory


class Video2012Factory(Factory):
    FACTORY_FOR = models.Video2012

    title = 'Test'
    description = 'Test description'
    category = 'test'
    region = 'test'
    upload_url = 'http://example.com'
    shortlink = 'test_shortlink'
    state = 'complete'
    votes = 0
