import datetime
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.http import JsonResponse
from osler.workup.models import Workup
from osler.datadashboard import models


class DataDashboardView(TemplateView):
    template_name = 'datadashboard/patient_data_dashboard.html'


def query_hypertension_workups():
    '''Queries all workups defined as hypertensive (currently defined as bp_sys > 100)'''
    hypertensive_workups = Workup.objects.filter(diagnosis__contains='hypertension').\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    return hypertensive_workups


def query_diabetes_workups():
    '''Queries all workups defined as diabetic under diagnosis field'''
    diabetic_workups = Workup.objects.filter(diagnosis__contains='diabetes').\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    return diabetic_workups


def query_all_workups():
    '''Queries all workups'''
    diabetic_workups = Workup.objects.all().\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    return diabetic_workups


def extract_demographic_data(workups):
    '''takes in queryed workups then extracts and formats related demographic data into json friendly format'''
    dashboard_data = {}
    unique_patient_pk_list = []
    for wu in workups:
        demographics = {}
        if wu.patient.pk not in unique_patient_pk_list:
            unique_patient_pk_list.append(wu.patient.pk)
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


def send_json(request):
    all_workups = query_all_workups()
    dashboard_data = extract_demographic_data(all_workups)
    return JsonResponse(dashboard_data)


def send_hypertension_json(request):
    hypertensive_workups = query_hypertension_workups()
    dashboard_data = extract_demographic_data(hypertensive_workups)
    return JsonResponse(dashboard_data)


def send_diabetes_json(request):
    diabetes_workups = query_diabetes_workups()
    dashboard_data = extract_demographic_data(diabetes_workups)
    return JsonResponse(dashboard_data)
