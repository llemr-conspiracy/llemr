from django.contrib import admin
from . import models

# Register your models here.
for model in [models.Language, models.Patient,
              models.Provider, models.ClinicDate,
              models.Workup, models.Followup]:
    admin.site.register(model)
