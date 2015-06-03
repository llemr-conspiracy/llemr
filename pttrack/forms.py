from django import forms
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
        exclude = ['patient', 'written_date', 'author']


class ActionItemForm(ModelForm):
    class Meta:
        model = models.ActionItem
        exclude = ['done', 'author', 'written_date', 'patient']


class ClinicDateForm(ModelForm):
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']
