# from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import ModelForm

from . import models


class PatientForm(ModelForm):
    class Meta:
        model = models.Patient
        exclude = []


class WorkupForm(ModelForm):
    class Meta:
        model = models.Workup
        exclude = ['patient', 'clinic_day', 'author']


class FollowupForm(ModelForm):
    class Meta:
        model = models.Followup
        exclude = ['patient', 'written_datetime', 'author']


class ActionItemForm(ModelForm):
    class Meta:
        model = models.ActionItem
        exclude = ['completion_date', 'author', 'written_date', 'patient', 'completion_author']
        widgets = {'due_date': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                       "pickTime": False})}


class ClinicDateForm(ModelForm):
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']
