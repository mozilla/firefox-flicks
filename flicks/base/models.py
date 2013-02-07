from django.conf import settings
from django.db import models

from product_details import product_details


ENGLISH_LANGUAGE_CHOICES = sorted(
    [(key.lower(), u'{0} ({1})'.format(key, value['English']))
     for key, value in product_details.languages.items()]
)

ENGLISH_COUNTRY_CHOICES = sorted(
    [(code, u'{0} ({1})'.format(code, name)) for code, name in
     product_details.get_regions('en-US').items()
     if code not in settings.INELIGIBLE_COUNTRIES]
)


class LocaleField(models.CharField):
    description = ('CharField with locale settings specific to Flicks '
                   'defaults.')

    def __init__(self, *args, **kwargs):
        options = {
            'max_length': 32,
            'default': settings.LANGUAGE_CODE,
            'choices': ENGLISH_LANGUAGE_CHOICES
        }
        options.update(kwargs)
        return super(LocaleField, self).__init__(*args, **options)


class CountryField(models.CharField):
    description = ('CharField with country settings specific to Flicks '
                   'defaults.')

    def __init__(self, *args, **kwargs):
        options = {
            'max_length': 16,
            'default': u'us',
            'choices': ENGLISH_COUNTRY_CHOICES
        }
        options.update(kwargs)
        return super(CountryField, self).__init__(*args, **options)


# South introspection rules for custom fields
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ['^flicks\.base\.models\.LocaleField'])
add_introspection_rules([], ['^flicks\.base\.models\.CountryField'])
