from __future__ import unicode_literals
from django.contrib import admin
from osler.utils.admin import NoteAdmin
from . import models

admin.site.register(models.Drug)

admin.site.register(models.DrugCategory)

admin.site.register(models.MeasuringUnit)

admin.site.register(models.Manufacturer)

admin.site.register(models.DispenseHistory, NoteAdmin)
