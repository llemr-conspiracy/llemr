from django.contrib import admin
from adminsortable.admin import SortableAdmin

from osler.utils import admin as admin_utils
from osler.core import models


for model in [models.Language, models.Patient,
              models.Gender, models.ActionInstruction, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome, models.EncounterStatus]:
    admin_utils.simplehistory_aware_register(model)

admin.site.register(models.Document, admin_utils.NoteAdmin)
admin.site.register(models.ActionItem, admin_utils.ActionItemAdmin)


@admin.register(models.Encounter)
class EncounterAdmin(SortableAdmin):
    #made a custom so I could javascript fix the url idk why
    sortable_change_list_template = 'adminsortable/custom_change_list.html'