'''
Validators for the Workups subapp.
'''

from django.core.exceptions import ValidationError

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
        temperature = float(value)
    except ValueError:
        raise ValidationError(
            str(value) + " is not a decimal value")

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
