from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from . import models


@admin.register(models.Appointment)
class ClinicDateAdmin(SimpleHistoryAdmin):
    date_hierarchy = 'clindate'
    list_display = ('__str__', 'clindate', 'clintime', 'appointment_type')
