'''
Validators for the Workups subapp.
'''

from django.core.exceptions import ValidationError


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
        raise ValidationError("".join([
            "The systolic blood pressure (", str(top),
            ") has to be higher than the diastolic blood pressure (",
            str(bottom), ")."]))
