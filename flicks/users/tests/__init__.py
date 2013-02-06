from django.contrib.auth.models import Group, User

from factory import Factory, Sequence, SubFactory

from flicks.users.models import UserProfile


class UserFactory(Factory):
    FACTORY_FOR = User

    username = Sequence(lambda n: 'test{0}'.format(n))


class GroupFactory(Factory):
    FACTORY_FOR = Group

    name = Sequence(lambda n: 'test{0}'.format(n))


class UserProfileFactory(Factory):
    FACTORY_FOR = UserProfile

    user = SubFactory(UserFactory)
    full_name = Sequence(lambda n: 'test{0}'.format(n))
    nickname = Sequence(lambda n: 'test{0}'.format(n))
    country = 'us'
