from __future__ import unicode_literals
from django.contrib import admin

from osler.utils.admin import NoteAdmin, simplehistory_aware_register
from . import models


for model in [models.VaccineSeriesType, models.VaccineDoseType]:
    simplehistory_aware_register(model)

for model in [models.VaccineSeries, models.VaccineDose, models.VaccineActionItem, models. VaccineFollowup]:
    admin.site.register(model, NoteAdmin)
