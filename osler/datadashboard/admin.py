from django.contrib import admin
from django.utils.timezone import now

from osler.workup.models import Workup
from osler.datadashboard import models
import datetime


@admin.register(models.PatientDataSummary)
class PatientDataDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/patient_data_dashboard_change_list.html"
    # date_hierarchy = 'added_on'

    # is it ok to be doing the query globally? Should we put it in a function that's called in the main (changelist_view)?
    hypertensive_workups = Workup.objects.filter(bp_sys__gte=140).\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    # by doing select_related, we minimize the amount of times we have to hit the database, decreasing runtime

# for now we will just define a patient as hypertensive if they have a single workup of bp_sys > 140, 
# but eventually this method could be modified to be a more robust way of checking for hypertension
    # def check_if_hypertensive(self,patient_pk):
    #         patient_workups = self.hypertensive_workups.filter(patient=patient_pk)
    #         # maybe switch this to a ratio (ex. if > 50% of workups are hypertensive then it counts)

    #         print(patient_workups.count())
    #         if patient_workups.count() >= 2:
    #             return True
    #         else:
    #             return False

    def changelist_view(self, request, extra_context=None):
        response = super(PatientDataDashboardAdmin, self).changelist_view(
            request, extra_context)

        # for h in hypertensive_workups:
        #     print(h.pk)
        # self.check_if_hypertensive(99)

        dashboard_data = {}
        unique_patient_pk_list = []

        for wu in self.hypertensive_workups:
            demographics = {}
            if wu.pk not in unique_patient_pk_list:
                unique_patient_pk_list.append(wu.pk)
                # if self.check_if_hypertensive(wu.patient):
                demographics['age'] = (now().date() - wu.patient.date_of_birth).days // 365
                demographics['gender'] = wu.patient.gender.name
                demographics['ethnicity'] = ", ".join(str(ethnicity) for ethnicity in wu.patient.ethnicities.all())
                dashboard_data[wu.patient.name()] = demographics
        response.context_data['data'] = dict(
            dashboard_data
        )
        return response
