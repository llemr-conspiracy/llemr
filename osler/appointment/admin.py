from osler.utils.admin import simplehistory_aware_register
from . import models

for model in [models.Appointment]:
    simplehistory_aware_register(model)
