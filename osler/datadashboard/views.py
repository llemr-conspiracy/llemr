from django.shortcuts import render
from django.utils.timezone import now
from osler.workup.models import Workup
from osler.datadashboard import models
import datetime
from json import dumps

def get_dashboard_data(filtered_workups):
    dashboard_data = []
    unique_patient_pk_list = []
    for wu in filtered_workups:
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
            dashboard_data.append(demographics)
    return dashboard_data


def display_hypertensive(request):
    '''Queries all workups defined as hypertensive (currently defined as bp_sys > 140) 
    and formats related patient demographic data into a json to be rendered in template'''
    workup_data = {}
    workup_data['all'] = Workup.objects.all().count()
    # workup_data['got_voucher'] = Workup.objects.filter(got_voucher=True).count()

    hypertensive_workups = Workup.objects.filter(bp_sys__gte=140).\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')

    dashboard_data = get_dashboard_data(hypertensive_workups)

    data = dumps(dashboard_data)

    # should we do other "quick facts" like median age or gender distribution?

    context = {'workup_data': workup_data, 'data': data}
    return render(request, 'datadashboard/patient_data_dashboard.html', context)

def display_diabetes(request):
    '''Queries all workups defined as diabetic under diagnosis field
    and formats them into json template'''
    workup_data = {}
    workup_data['all'] = Workup.objects.all().count()  

    diabetic_workups = Workup.objects.filter(diagnosis__contains='diabetes').\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')

    print(diabetic_workups)

    dashboard_data = get_dashboard_data(diabetic_workups)

    data = dumps(dashboard_data)

    context = {'workup_data': workup_data, 'data':data}
    return render(request,'datadashboard/patient_data_dashboard.html',context)


def display_daterange(request):
    '''Queries all workups in a given timerange defined as hypertensive (currently just hypertensive patients, in future different kinds of diseases)'''
    start_date = "2020-01-01"  # take these values from form
    end_date = '2020-04-04'
    workups = Workup.objects.filter(date_range=[start_date, end_date]).filter(bp_sys__gte=140).\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')

    dashboard_data = get_dashboard_data(hypertensive_workups)

    data = dumps(dashboard_data)

    context = {'data': data}
    return render(request, 'datadashboard/patient_data_dashboard.html', context)
