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


def validate_hr(value):
    '''validate that a value is a valid heart rate'''
    try:
        heart_rate = int(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a integer")

    if heart_rate < 1:
        raise ValidationError(
            str(value) + " is not a positive number")

def validate_rr(value):
    '''validate that a value is a valid respiratory rate'''
    try:
        r_rate = int(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a integer")

    if r_rate < 1:
        raise ValidationError(
            str(value) + " is not a positive number")

def validate_t(value):
    '''validate that a value is a valid temperature'''
    try:
        temperature = int(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a integer")

    if temperature < 1:
        raise ValidationError(
            str(value) + " is not a positive number")

def validate_height(value):
    '''validate that a value is a valid temperature'''
    try:
        height = int(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a integer")

    if height < 1:
        raise ValidationError(
            str(value) + " is not a positive number")

def validate_weight(value):
    '''validate that a value is a valid temperature'''
    try:
        weight = int(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a integer")

    if weight< 1:
        raise ValidationError(
            str(value) + " is not a positive number")
