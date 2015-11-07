'''Custom validators for Osler.'''
import datetime
from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_ssn(value):
    '''Validate an SSN. Check length, and that it's only numbers except for hyphens at positions 3 and 6.'''

    init_value = value

    HYPHEN_1 = value.find('-')
    HYPHEN_2 = value.rfind('-')

    if HYPHEN_1 == 3:
        value = value[0:HYPHEN_1] + value[HYPHEN_1+1:]
    if HYPHEN_2 == 6:
        # have adapt for the possibility (or not) that hyphen 1 is there
        value = value[0:value.rfind('-')] + value[value.rfind('-')+1:]

    if '-' in value:
        raise ValidationError("Did you misplace a hyphen in '{0}'?".format(
            init_value))
    if not value.isdigit():
        raise ValidationError(" ".join(
            ['{0} is not a valid SSN. Your SSN shoud consist only of digits ',
             'with the form xxx-xx-xxxx (hyphens optional).']).format(init_value))
    if len(value) > 9:
        raise ValidationError(" ".join([
            '{0} is not a valid SSN, since it is longer than 9 characters.'
            ]).format(init_value))


def validate_zip(value):
    '''verify that the given value is in the ZIP code format'''
    if len(str(value)) != 5:
        raise ValidationError('{0} is not a valid ZIP, because it has {1}' +
                              ' digits.'.format(str(value), len(str(value))))

    if not str(value).isdigit():
        raise ValidationError(
            "%s is not a valid ZIP, because it contains non-digit characters."
            % value)


def validate_bp(value):
    '''validate that a value is a valid blood pressure'''
    try:
        (top, bottom) = value.split('/')
    except ValueError:
        raise ValidationError(
            str(value) + " is not a validly formatted blood pressure since " +
            "it cannot be split into two values using '/'.")

    try:
        (top, bottom) = (int(top), int(bottom))
    except ValueError:
        raise ValidationError(
            "Either '" + str(top) + "' or '" + str(bottom) + "' is not a " +
            "valid pressure--they must be small, positive integers.")

    if top < bottom:
        raise ValidationError(
            "The systolic blood pressure (" + str(top) +
            ") has to be higher than the diastolic blood pressure (" +
            str(bottom) + ").")


def validate_birth_date(value):
    today = now().date()

    if today - value < datetime.timedelta(0):
        raise ValidationError("Birth dates cannot be in the future.")

    if today - value > datetime.timedelta(365 * 150):
        raise ValidationError("Birth dates cannot be more than 150 years in the past.")


def validate_attending(value):
    return value.can_attend

