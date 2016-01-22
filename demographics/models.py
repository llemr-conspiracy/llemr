from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from pttrack.models import Patient

# Create your models here.

class IncomeRange(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class EducationLevel(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class WorkStatus(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class ResourceAccess(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class ChronicCondition(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class TransportationOption(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class Demographics(models.Model):

    patient= models.OneToOneField(Patient, null=True)

    creation_date = models.DateField(blank=True,null=True)

    chronic_condition = models.ManyToManyField(ChronicCondition, blank=True, null=True)

    has_insurance = models.BooleanField(default=False)

    ER_visit_last_year = models.BooleanField(default=False, verbose_name="Visited ER in the past year")

    last_date_physician_visit = models.DateField(blank=True,null=True, verbose_name="Date Last Visited Patient")

    resource_access = models.ManyToManyField(ResourceAccess, blank=True,
                                                 null=True, verbose_name="Access to Resources")

    lives_alone = models.BooleanField(default=False)

    dependents = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Number of Dependents")

    currently_employed = models.BooleanField(default=False)

    work_status = models.ForeignKey(WorkStatus, blank=True,null=True)

    education_level = models.ForeignKey(EducationLevel, blank=True,null=True)

    annual_income = models.ForeignKey(IncomeRange, blank=True,null=True)

    transportation = models.ForeignKey(TransportationOption, blank=True,null=True)