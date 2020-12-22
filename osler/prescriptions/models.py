from django.db import models
from django import forms
from osler.inventory.models import Drug
# current plan is to just make each attribute a separate model and then 
class Prescription(models.Model):
    # name = PrescritionModelField()
    name = models.ForeignKey(Drug, on_delete=models.PROTECT)
    dose = models.CharField()
    def __str__(self):
        return self.name()





