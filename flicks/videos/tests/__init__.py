import factory

from flicks.users.tests import UserFactory
from flicks.videos import models


class Video2013Factory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Video

    user = factory.SubFactory(UserFactory)
    title = 'Test title'
    description = 'Test desc'
    vimeo_id = factory.Sequence(lambda n: int(n))
    filename = factory.Sequence(lambda n: '{0}.mp4'.format(n))

    @factory.post_generation
    def vote_count(self, create, extracted, **kwargs):
        if create and extracted:
            for k in range(extracted):
                models.Vote.objects.create(video=self,
                                           user=UserFactory.create())
VideoFactory = Video2013Factory


class Video2012Factory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Video2012

    title = 'Test'
    description = 'Test description'
    category = 'test'
    region = 'test'
    upload_url = 'http://example.com'
    shortlink = 'test_shortlink'
    state = 'complete'
    votes = 0
