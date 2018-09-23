from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models


class NoteAdmin(SimpleHistoryAdmin):
    readonly_fields = ('written_datetime', 'last_modified', 'author',
                       'author_type')


# Register your models here.
for model in [models.Language, models.Patient, models.Provider,
              models.ProviderType, models.ActionInstruction, models.Ethnicity,
              models.Gender, models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)

for model in [models.ActionItem, models.Document]:
    admin.site.register(model, NoteAdmin)
