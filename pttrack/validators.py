'''Custom validators for Osler.'''

import datetime
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.apps import apps


def validate_zip(value):
    '''verify that the given value is in the ZIP code format'''
    if len(str(value)) != 5:
        raise ValidationError('{0} is not a valid ZIP, because it has {1}' +
                              ' digits.'.format(str(value), len(str(value))))

    if not str(value).isdigit():
        raise ValidationError(
            "%s is not a valid ZIP, because it contains non-digit characters."
            % value)


def validate_birth_date(value, max_years=150):
    '''
    Validate birtdays, requiring that they be 1) in the past and 2) less than
    max_years ago.
    '''
    today = now().date()

    if today - value < datetime.timedelta(0):
        raise ValidationError("Birth dates cannot be in the future.")

    if today - value > datetime.timedelta(365 * max_years):
        raise ValidationError(
            "Birth dates cannot be more than {0} years in the past.".format(
                max_years))


def validate_name(value):
    '''
    To validate that name (first, last middle) does not start or end with a
    space or tab
    '''

    if value.startswith((' ', '\t')) or value.endswith((' ', '\t')):
        raise ValidationError("Name cannot start or end with a space")


def validate_attending(value):
    '''
    Verify that a provider has attending priviledges.
    '''

    Provider = apps.get_model('pttrack', 'Provider')
    attending = Provider.objects.get(pk=value)

    if not attending.clinical_roles.filter(signs_charts=True).exists():
        raise ValidationError("This provider is not allowed to sign charts.")
