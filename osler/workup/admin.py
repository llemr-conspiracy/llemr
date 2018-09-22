from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models

class NoteAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified')

for model in [models.ClinicDate, models.ClinicType, models.DiagnosisType]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)

for model in [models.Workup, models.ProgressNote]:
    admin.site.register(model, NoteAdmin)