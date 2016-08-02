'''
Validators for the Workups subapp.
'''

from django.core.exceptions import ValidationError

MAX_SYSTOLIC = 400
MIN_DIASOLIC = 40


def validate_bp(value):
    '''validate that a value is a valid blood pressure'''
    try:
        (systolic, diastolic) = value.split('/')
    except ValueError:
        raise ValidationError(
            str(value) + " is not a validly formatted blood pressure since " +
            "it cannot be split into two values using '/'.")

    try:
        (systolic, diastolic) = (int(systolic), int(diastolic))
    except ValueError:
        raise ValidationError(
            "Either %s or %s is not a small, positive integer." %
            (systolic, diastolic))
    if systolic < diastolic:
        raise ValidationError("".join([
            "The systolic blood pressure (", str(systolic),
            ") has to be higher than the diastolic blood pressure (",
            str(diastolic), ")."]))

    if systolic > MAX_SYSTOLIC:
        raise ValidationError(
            "Systolic bp (%s) is unreasonably high." % systolic)

    if diastolic < MIN_DIASOLIC:
        raise ValidationError(
            "Diastolic bp (%s) is unreasonably low." % diastolic)
