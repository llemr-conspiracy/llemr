from django.contrib import admin

from osler.utils import admin as admin_utils
from osler.core import models

import osler.users.models as user_models

for model in [user_models.Language, models.Patient,
              user_models.Gender, models.ActionInstruction, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome]:
    admin_utils.simplehistory_aware_register(model)

admin.site.register(models.Document, admin_utils.NoteAdmin)
admin.site.register(models.ActionItem, admin_utils.ActionItemAdmin)
