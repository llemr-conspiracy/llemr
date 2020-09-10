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

        patient_data = {
            # 'age': age(qs.values('date_of_birth'))
            # (now().date() - qs.values('date_of_birth')).days // 365
            # 'name': models.Person.gender(self)
        }
        
        # for patient in patients:
        #     patient.
        # for patient in models.Patient.objects.raw('SELECT * FROM core_patient'):
        #     print(patient.gender)
        q = Workup.objects.all()
        print(q[0].bp_sys)
        
        response.context_data['age'] = list(
            q
            # .annotate(**patient_data)
        )
        

        return response
