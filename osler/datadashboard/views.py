import datetime
import json
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.http import JsonResponse
from osler.core.models import Encounter
from osler.demographics.models import Demographics
from osler.users.decorators import active_permission_required
from osler.workup.models import Workup
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.utils.decorators import method_decorator


homeless_address = '3151 Olive St.'
ethnicity_list = []
zip_code_list = []
@method_decorator(active_permission_required('users.view_clinic_datadashboard', raise_exception=True), name='dispatch')
class DataDashboardView(TemplateView):
    template_name = 'datadashboard/data_dashboard.html'        


def send_patientdata_json(request):
    '''Sends patient and workup related data to be used in main dashboard data charts'''
    all_workups = query_workups_model()
    all_demographics = query_demographics_model()
    dashboard_data = extract_demographic_data(all_workups, all_demographics)
    return JsonResponse(dashboard_data)

def query_workups_model():
    '''Queries all workups and extracts demographic data'''
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
    '''takes in queryed workups then extracts and formats related demographic data into json friendly formating
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
            demographics['age'] = (wu.written_datetime.date() - wu.patient.date_of_birth).days // 365
            demographics['gender'] = wu.patient.gender.name
            if(wu.patient.address != homeless_address):
                demographics['zip_code'] = wu.patient.zip_code
            else:
                demographics['zip_code'] = None
            if(wu.patient.zip_code not in zip_code_list):
              zip_code_list.append(wu.patient.zip_code)
            ethnicities = []
            for ethnicity in list(wu.patient.ethnicities.all()):
                if(ethnicity not in ethnicity_list):
                  ethnicity_list.append(ethnicity)
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


def send_context_json(request):
    ''' Formats context data such as clinic dates for json '''
    context = {}
    context["clinic_dates"] = json.dumps(list_clinic_dates())
    context["num_ethnicities"] = len(ethnicity_list)
    context["num_zipcodes"] = len(zip_code_list)
    return JsonResponse(context)

def list_clinic_dates():
    '''Queries all Encounters and filters them into a date ordered list of unique dates in which patients were seen
    serves as a proxy to the old ClinicDate model
    '''
    raw_encounters = Encounter.objects.all()
    dates = []
    for encounter in raw_encounters:
        date = datetime.datetime.strftime(getattr(encounter, "clinic_day"), "%Y-%m-%d")
        if date not in dates:
          dates.append(date)
    dates.sort()
    return dates
