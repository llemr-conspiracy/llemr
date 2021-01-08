from django.db import models
from osler.core.models import Patient


class PatientDataSummary(Patient):
    class Meta:
        proxy = True
        verbose_name = 'Patient Data Dashboard'
        verbose_name_plural = 'Patient Data Dashboard'
