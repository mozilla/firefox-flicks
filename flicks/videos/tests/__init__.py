from factory import Factory

from flicks.videos import models


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
