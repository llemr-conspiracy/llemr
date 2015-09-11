
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models
from . import followup_models

# Register your models here.
for model in [models.Language, models.Patient, models.Provider,
              models.ClinicDate, models.Workup, models.ClinicType,
              models.ActionInstruction, models.ActionItem, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.Document, models.DocumentType]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)

for model in [followup_models.ReferralFollowup, followup_models.NoShowReason,
              followup_models.NoAptReason, followup_models.ContactResult,
              followup_models.LabFollowup, followup_models.VaccineFollowup,
              followup_models.GeneralFollowup]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
