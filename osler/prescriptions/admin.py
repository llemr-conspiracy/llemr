from __future__ import unicode_literals
from django.contrib import admin
from django.urls import reverse

from osler.utils import admin as admin_utils
from . import models


@admin.register(models.Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('drug_name','dose', 'frequency', 'route')
