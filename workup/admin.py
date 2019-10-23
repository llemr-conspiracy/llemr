from django.contrib import admin
from django.core.urlresolvers import reverse
from simple_history.admin import SimpleHistoryAdmin

from pttrack.admin import NoteAdmin
from . import models


@admin.register(models.ClinicDate)
class ClinicDateAdmin(admin.ModelAdmin):
    date_hierarchy = 'clinic_date'
    list_display = ('__str__', 'clinic_date', 'clinic_type', 'number_of_notes')


@admin.register(models.Workup)
class WorkupAdmin(NoteAdmin):
    date_hierarchy = 'written_datetime'

    list_display = ('chief_complaint', 'written_datetime', 'patient',
                    'author', 'clinic_day', 'attending', 'signed')

    readonly_fields = NoteAdmin.readonly_fields + ('author', 'signed_date',
                                                   'signer')
    list_filter = ('clinic_day', 'diagnosis_categories')
    search_fields = ('patient__first_name', 'patient__last_name',
                     'attending__first_name', 'attending__last_name',
                     'author__first_name', 'author__last_name',
                     'clinic_day__clinic_type__name',
                     'chief_complaint')

    def view_on_site(self, obj):
        url = reverse('workup', kwargs={'pk': obj.pk})
        return url


@admin.register(models.ProgressNote)
class ProgressNoteAdmin(NoteAdmin):

    def view_on_site(self, obj):
        url = reverse('progress-note-detail', kwargs={'pk': obj.pk})
        return url


for model in [models.ClinicType, models.DiagnosisType]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
