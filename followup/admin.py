from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from . import models

for model in [models.ReferralFollowup, models.NoShowReason,
              models.NoAptReason, models.ContactResult,
              models.LabFollowup, models.VaccineFollowup,
              models.GeneralFollowup]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
