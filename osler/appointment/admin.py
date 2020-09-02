from django.conf import settings
from osler.utils.admin import simplehistory_aware_register
from . import models

if settings.DISPLAY_APPOINTMENTS:
    for model in [models.Appointment]:
        simplehistory_aware_register(model)
