from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models


class NoteAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')


for model in [models.Referral, models.FollowupRequest, models.PatientContact]:
    admin.site.register(model, NoteAdmin)
