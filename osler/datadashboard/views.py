import datetime
from json import dumps
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.http import JsonResponse
from osler.workup.models import Workup
from osler.datadashboard import models

class DataDashboardView(TemplateView):
    template_name = 'datadashboard/patient_data_dashboard.html'        

def query_hypertensive_demographics():
    '''Queries all workups defined as hypertensive (currently defined as bp_sys > 100) 
    and formats related patient demographic data into a json to be rendered in template'''
    workup_data = {}
    workup_data['all'] = Workup.objects.all().count()
    # workup_data['got_voucher'] = Workup.objects.filter(got_voucher=True).count()

    hypertensive_workups = Workup.objects.filter(bp_sys__gte=100).\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')
    return hypertensive_workups

def send_json(request):
    # passing the department choices to the template in the context
    hypertensive_workups = query_hypertensive_demographics()
    print(hypertensive_workups)
    dashboard_data = {}
    unique_patient_pk_list = []
    for wu in hypertensive_workups:
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
    return JsonResponse(dashboard_data)

# def display_daterange(request):
#     '''Queries all workups in a given timerange defined as hypertensive (currently just hypertensive patients, in future different kinds of diseases)'''
#     start_date = "2020-01-01"  # take these values from form
#     end_date = '2020-04-04'
#     workups = Workup.objects.filter(date_range=[start_date, end_date]).filter(bp_sys__gte=100).\
#         select_related('patient').\
#         select_related('patient__gender').\
#         prefetch_related('patient__ethnicities')

#     dashboard_data = get_dashboard_data(hypertensive_workups)

#     data = dumps(dashboard_data)

#     context = {'data': data}
#     return render(request, 'datadashboard/patient_data_dashboard.html', context)
