import datetime
import json
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.http import JsonResponse
from osler.demographics.models import Demographics
from osler.workup.models import Workup
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse

class DataDashboardView(TemplateView):
    template_name = 'datadashboard/patient_data_dashboard.html'        

# def query_clinic_dates_model():
#     raw_clinic_dates = ClinicDate.objects.all()
#     dates = []
#     for clinic in raw_clinic_dates:
#         dates.append(datetime.datetime.strftime(getattr(clinic, "clinic_date"),"%Y-%m-%d"))
#     dates.sort()
#     return dates

def query_workups_model():
    '''Queries all workups'''
    return Workup.objects.all().\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    
def query_demographics_model():
    raw_demographics = Demographics.objects.all()
    formatted_demographics = {}
    for demographic in raw_demographics:
        conditions = []
        for condition in list(demographic.chronic_conditions.all()):
                conditions.append(getattr(condition, 'name'))
        formatted_demographics[demographic.pk] = conditions
    return formatted_demographics

def extract_demographic_data(workups,demo):
    '''takes in queryed workups then extracts and formats related demographic data into json friendly format, 
    also extracts unique clinic dates into a list
    '''
    dashboard_data = {}
    unique_patient_pk_list = []
    for wu in workups:
        demographics = {}
        if wu.patient.pk not in unique_patient_pk_list:
            unique_patient_pk_list.append(wu.patient.pk)
            if(wu.patient.pk in demo):
                demographics['conditions'] = demo[wu.patient.pk]
            else:
                demographics['conditions'] = []
            demographics['age'] = (now().date() - wu.patient.date_of_birth).days // 365
            demographics['gender'] = wu.patient.gender.name
            ethnicities = []
            for ethnicity in list(wu.patient.ethnicities.all()):
                ethnicities.append(getattr(ethnicity, 'name'))
            demographics['ethnicities'] = ethnicities
            demographics['name'] = wu.patient.name()
            demographics['wu_dates'] = [str(wu.written_datetime.date())]
            dashboard_data[wu.patient.pk] = demographics
        else:
            # adds repeat workups to date list to be used in js side date filtering
            existing_wu_dates = dashboard_data.get(wu.patient.pk)['wu_dates']
            existing_wu_dates.append(str(wu.written_datetime.date()))
    return dashboard_data

def send_all_json(request):
    '''Sends patient and workup related data to be used in main dashboard data charts'''
    all_workups = query_workups_model()
    all_demographics = query_demographics_model()
    dashboard_data = extract_demographic_data(all_workups,all_demographics)
    return JsonResponse(dashboard_data)
