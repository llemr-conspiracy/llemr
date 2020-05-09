from osler.utils.admin import simplehistory_aware_register
from . import models

for model in [models.IncomeRange, models.EducationLevel, models.WorkStatus,
              models.ResourceAccess, models.ChronicCondition,
              models.TransportationOption, models.Demographics]:
    simplehistory_aware_register(model)
