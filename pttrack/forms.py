from django import forms
from django.forms import ModelForm

from . import models


class PatientForm(ModelForm):
    class Meta:
        model = models.Patient
        exclude = []
