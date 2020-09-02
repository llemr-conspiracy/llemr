from django.conf import settings
from django.contrib import admin

from osler.utils.admin import NoteAdmin
from . import models

if settings.DISPLAY_REFERRALS:
    for model in [models.Referral, models.FollowupRequest, models.PatientContact]:
        admin.site.register(model, NoteAdmin)
