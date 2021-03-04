'''
Validators for the Workups subapp.
'''
from __future__ import unicode_literals

from builtins import str
from django.conf import settings
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


def validate_bp_systolic(value):
    if value > settings.OSLER_MAX_SYSTOLIC:
        raise ValidationError(
            _("Systolic BP %(value)s is higher than the maximum allowed value (%(allowed_value)s).")
            % {'value': value, 'allowed_value': settings.OSLER_MAX_SYSTOLIC})


def validate_bp_diastolic(value):
    if value < settings.OSLER_MIN_DIASTOLIC:
        raise ValidationError(
            _("Diastolic BP %(value)s is lower than the minimum allowed value (%(allowed_value)s).")
            % {'value': value, 'allowed_value': settings.OSLER_MIN_DIASTOLIC})


########################
#    WILL BE REMOVED   #
########################

def validate_hr(value):
    '''validate that a value is a valid heart rate'''
    try:
        heart_rate = int(value)
    except ValueError:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a integer")))

    if heart_rate < 1:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a positive number")))


def validate_rr(value):
    '''validate that a value is a valid respiratory rate'''
    try:
        r_rate = int(value)
    except ValueError:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a integer")))

    if r_rate < 1:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a positive number")))


def validate_t(value):
    '''validate that a value is a valid temperature'''
    try:
        temperature = float(value)
    except ValueError:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a decimal value")))

    if temperature < 1:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a positive number")))


def validate_height(value):
    '''validate that a value is a valid temperature'''
    try:
        height = int(value)
    except ValueError:
        raise ValidationError(
            "%s %s" % (str(value), _(" is not a integer")))

    if height < 1:
        raise ValidationError(
            "%s %s" % (str(value), _("is not a positive number")))


def validate_weight(value):
    '''validate that a value is a valid temperature'''
    try:
        weight = int(value)
    except ValueError:
        raise ValidationError(
            "%s %s" % (str(value), _("is not a integer")))

    if weight < 1:
        raise ValidationError(
            "%s %s" % (str(value), _("is not a positive number")))
