from __future__ import unicode_literals
from django.contrib import admin
from osler.utils.admin import NoteAdmin
from osler.utils import admin as admin_utils
from . import models
from simple_history.admin import SimpleHistoryAdmin

for model in [models.DrugCategory, models.MeasuringUnit, models.Manufacturer]:
    admin.site.register(model)

admin.site.register(models.Drug, SimpleHistoryAdmin)

admin.site.register(models.DispenseHistory, NoteAdmin)
