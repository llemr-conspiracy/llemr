from django.utils.timezone import now
from django.contrib import admin

from osler.utils import admin as admin_utils
from osler.core import models
from osler.workup.models import Workup
import datetime


for model in [models.Language, models.Patient,
              models.Gender, models.ActionInstruction, models.Ethnicity,
              models.ReferralType, models.ReferralLocation,
              models.ContactMethod, models.DocumentType, models.Outcome]:
    admin_utils.simplehistory_aware_register(model)

admin.site.register(models.Document, admin_utils.NoteAdmin)
admin.site.register(models.ActionItem, admin_utils.ActionItemAdmin)


@admin.register(models.PatientDataSummary)
class PatientDataDashboardAdmin(admin.ModelAdmin):
    # change_list_template = 'admin/sale_summary_change_list.html'
    change_list_template = "admin/patient_data_dashboard_change_list.html"

    def changelist_view(self, request, extra_context=None):
        response = super(PatientDataDashboardAdmin, self).changelist_view(
            request, extra_context)

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        patients = models.Patient.objects.all()

        dashboard_data = {}

        hypertensive_workups = Workup.objects.filter(bp_sys__gte=140)
        hypertensive_patients = list(hypertensive_workups.values_list('patient', flat=True))
        for pk in hypertensive_patients:
            patient = patients.filter(pk=pk)[0]  # initializes patient
            workups = Workup.objects.filter(patient=pk)  # finds all the workups for this particular patient
            current_workup = None
            demographics = {}

            for w in workups:  # finds the latest workup. alternative to latest_workup function
                if(current_workup == None):
                    current_workup = w
                else:
                    w_days = (now()-w.last_modified).days
                    current_days = (now()-current_workup.last_modified).days
                    if(w_days < current_days):
                        current_workup = w

            demographics['bp_sys'] = current_workup.bp_sys
            demographics['age'] = (now().date() - patient.date_of_birth).days // 365
            demographics['gender'] = patient.gender.name
            demographics['ethnicity'] = patient.ethnicities
            dashboard_data[patient.name()] = demographics

        frankie = patients.filter(pk=1)
        # gets workups based on patient pk (aka get frankie's workups)
        workups = Workup.objects.filter(patient__in=list(frankie.values_list('pk', flat=True)))
        # models.PatientDataSummary.objects.create(bp_readings=[130,120,150])

        response.context_data['data'] = dict(
            dashboard_data
        )

        return response
