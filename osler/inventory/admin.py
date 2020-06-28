from __future__ import unicode_literals
from django.contrib import admin
from django.urls import reverse

from osler.utils import admin as admin_utils
from . import models

@admin.register(models.Drug)
class DrugAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DrugCategory)
class DrugCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MeasuringUnit)
class MeasuringUnitAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    pass
