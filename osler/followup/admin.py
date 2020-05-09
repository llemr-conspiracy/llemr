from __future__ import unicode_literals
from django.contrib import admin

from osler.utils.admin import NoteAdmin, simplehistory_aware_register
from . import models


for model in [models.NoShowReason, models.NoAptReason, models.ContactResult]:
    simplehistory_aware_register(model)

for model in [models.LabFollowup, models.VaccineFollowup,
              models.GeneralFollowup, models.ReferralFollowup]:
    admin.site.register(model, NoteAdmin)
