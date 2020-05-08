from __future__ import unicode_literals
from builtins import object
from django.db import models
from simple_history.models import HistoricalRecords

from pttrack.models import Patient

# Create your models here.


class IncomeRange(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class WorkStatus(models.Model):

    class Meta(object):
        verbose_name_plural = "Work statuses"

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class ResourceAccess(models.Model):

    class Meta(object):
        verbose_name_plural = "Resource accesses"

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class ChronicCondition(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class TransportationOption(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Demographics(models.Model):

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, null=True)

    creation_date = models.DateField(blank=True, null=True)

    chronic_condition = models.ManyToManyField(ChronicCondition, blank=True)

    has_insurance = models.BooleanField(null=True, blank=True)

    ER_visit_last_year = models.BooleanField(
        null=True, blank=True,
        verbose_name="Visited ER in the Past Year"
    )

    last_date_physician_visit = models.DateField(
        blank=True, null=True,
        verbose_name="Date of Patient's Last Visit to Physician or ER")

    resource_access = models.ManyToManyField(
        ResourceAccess, blank=True,
        verbose_name="Access to Resources")

    lives_alone = models.BooleanField(null=True, blank=True)

    dependents = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Number of Dependents")

    currently_employed = models.BooleanField(null=True, blank=True)

    work_status = models.ForeignKey(
        WorkStatus,
        on_delete=models.PROTECT,
        blank=True, null=True
    )

    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.PROTECT,
        blank=True, null=True)

    annual_income = models.ForeignKey(
        IncomeRange,
        on_delete=models.PROTECT,
        blank=True, null=True)

    transportation = models.ForeignKey(
        TransportationOption,
        on_delete=models.PROTECT,
        blank=True, null=True)

    history = HistoricalRecords()
