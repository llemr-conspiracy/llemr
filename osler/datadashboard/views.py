from django.shortcuts import render
from django.utils.timezone import now
from osler.workup.models import Workup
from osler.datadashboard import models
import datetime
from json import dumps


def display_hypertensive(request):
    '''Queries all workups defined as hypertensive (currently defined as bp_sys > 140) 
    and formats related patient demographic data into a json to be rendered in template'''

    hypertensive_workups = Workup.objects.filter(bp_sys__gte=140).\
        select_related('patient').\
        select_related('patient__gender').\
        prefetch_related('patient__ethnicities')

    dashboard_data = []
    unique_patient_pk_list = []

    for wu in hypertensive_workups:
        demographics = {}
        if wu.patient.pk not in unique_patient_pk_list:
            unique_patient_pk_list.append(wu.patient.pk)
            demographics['age'] = (now().date() - wu.patient.date_of_birth).days // 365
            demographics['gender'] = wu.patient.gender.name
            demographics['ethnicity'] = ", ".join(str(ethnicity) for ethnicity in wu.patient.ethnicities.all())
            demographics['name'] = wu.patient.name()
            dashboard_data.append(demographics)
    data = dumps(dashboard_data)
    return render(request, 'datadashboard/patient_data_dashboard.html', {"data": data})