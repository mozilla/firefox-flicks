from django.contrib.auth.models import Group, User

from factory import DjangoModelFactory, Sequence, SubFactory

from flicks.users.models import UserProfile


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = User

    username = Sequence(lambda n: 'test{0}'.format(n))


class GroupFactory(DjangoModelFactory):
    FACTORY_FOR = Group

    name = Sequence(lambda n: 'test{0}'.format(n))


class UserProfileFactory(DjangoModelFactory):
    FACTORY_FOR = UserProfile

    user = SubFactory(UserFactory)
    full_name = Sequence(lambda n: 'test{0}'.format(n))
    nickname = Sequence(lambda n: 'test{0}'.format(n))
    country = 'us'
