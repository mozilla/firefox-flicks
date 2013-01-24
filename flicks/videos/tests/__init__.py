from factory import Factory

from flicks.videos import models


class VideoFactory(Factory):
    FACTORY_FOR = models.Video

    title = 'Test'
    description = 'Test description'
    category = 'test'
    region = 'test'
    upload_url = 'http://example.com'
    shortlink = 'test_shortlink'
    state = 'complete'
    votes = 0
