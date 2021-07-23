import datetime
import json
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.http import JsonResponse
from osler.core.models import Encounter
from osler.demographics.models import Demographics
from osler.inventory.models import DispenseHistory
from osler.labs.models import Lab
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
        demo_data = {}
        conditions = []
        for condition in list(demographic.chronic_conditions.all()):
                conditions.append(getattr(condition, 'name'))
        demo_data["conditions"] = conditions
        demo_data["has_insurance"] = demographic.has_insurance
        formatted_demographics[demographic.pk] = demo_data
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
                demographics['conditions'] = demo[wu.patient.pk]['conditions']
            else:
                demographics['conditions'] = []
            demographics['has_insurance'] = demo[wu.patient.pk]['has_insurance']
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
    context["num_ethnicities"] = len(ethnicity_list)
    context["num_zipcodes"] = len(zip_code_list)
    context["clinic_dates"] = json.dumps(list_clinic_dates())
    context["drug_dispenses"] = query_drug_model()
    context["labs_ordered"] = query_labs_model()
    print(query_labs_model())
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

def query_drug_model():
    '''Queries inventory and extracts dispense history models'''
    dispense_list = {}
    dispenses = DispenseHistory.objects.all()
    for item in dispenses:
        written_date = datetime.datetime.strftime(getattr(item, "written_datetime"), "%Y-%m-%d")
        drug = getattr(item, "drug")
        drug_name = getattr(drug, "name")
        if(drug_name not in dispense_list):
          dispense_list[drug_name] = [written_date]
        else:
          dispense_list[drug_name].append(written_date)
    return dispense_list


def query_labs_model():
    '''Queries inventory and extracts dispense history models'''
    labs_list = {}
    labs = Lab.objects.all()
    for item in labs:
        written_date = datetime.datetime.strftime(getattr(item, "lab_time"), "%Y-%m-%d")
        lab_type = getattr(item, "lab_type")
        lab_type_name = getattr(lab_type, "name")
        if(lab_type_name not in labs_list):
          labs_list[lab_type_name] = [written_date]
        else:
          labs_list[lab_type_name].append(written_date)
    return labs_list
