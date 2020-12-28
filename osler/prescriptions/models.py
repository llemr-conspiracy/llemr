from django.db import models
from django import forms
from osler.inventory.models import Drug
from osler.core.models import Patient
class Prescription(models.Model):
    # name = PrescritionModelField()
    drug_name = models.ForeignKey(Drug, on_delete=models.PROTECT)
    dose = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=100, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.drug_name()
