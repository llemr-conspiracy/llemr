from django.conf import settings
from osler.utils.admin import simplehistory_aware_register
from . import models

if settings.OSLER_DISPLAY_APPOINTMENTS:
    for model in [models.Appointment]:
        simplehistory_aware_register(model)
