from django.contrib import admin

from osler.utils.admin import NoteAdmin
from . import models

for model in [models.Referral, models.FollowupRequest, models.PatientContact]:
    admin.site.register(model, NoteAdmin)
