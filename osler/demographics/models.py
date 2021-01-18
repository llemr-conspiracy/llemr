from django.db import models
from simple_history.models import HistoricalRecords

from osler.core.models import Patient

from django.utils.translation import gettext_lazy as _


class IncomeRange(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class WorkStatus(models.Model):

    class Meta:
        verbose_name_plural = _("Work statuses")

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class ResourceAccess(models.Model):

    class Meta:
        verbose_name_plural = _("Resource accesses")

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class ChronicCondition(models.Model):

    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class TransportationOption(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class Demographics(models.Model):

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, null=True, verbose_name=_("Patient"))

    creation_date = models.DateField(blank=True, null=True, verbose_name=_("Creation date"))

    chronic_conditions = models.ManyToManyField(ChronicCondition, blank=True, verbose_name=_("Chronic condition"))

    has_insurance = models.BooleanField(null=True, blank=True, verbose_name=_("Has insurance"))

    ER_visit_last_year = models.BooleanField(
        null=True, blank=True,
        verbose_name=_("Visited ER in the Past Year")
    )

    last_date_physician_visit = models.DateField(
        blank=True, null=True,
        verbose_name=_("Date of Patient's Last Visit to Physician or ER"))

    resource_access = models.ManyToManyField(
        ResourceAccess, blank=True,
        verbose_name=_("Access to Resources"))

    lives_alone = models.BooleanField(null=True, blank=True, verbose_name=_("Lives alone"))

    dependents = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name=_("Number of Dependents"))

    currently_employed = models.BooleanField(null=True, blank=True, verbose_name=_("Currently employed"))

    work_status = models.ForeignKey(
        WorkStatus,
        on_delete=models.PROTECT,
        blank=True, null=True, verbose_name=_("Work status")
    )

    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.PROTECT,
        blank=True, null=True, verbose_name=_("Education level"))

    annual_income = models.ForeignKey(
        IncomeRange,
        on_delete=models.PROTECT,
        blank=True, null=True, verbose_name=_("Annual income"))

    transportation = models.ForeignKey(
        TransportationOption,
        on_delete=models.PROTECT,
        blank=True, null=True, verbose_name=_("Transportation"))

    history = HistoricalRecords()
