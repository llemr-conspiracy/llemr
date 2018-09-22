from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models

for model in [models.IncomeRange, models.EducationLevel, models.WorkStatus,
              models.ResourceAccess, models.ChronicCondition,
              models.TransportationOption, models.Demographics]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
