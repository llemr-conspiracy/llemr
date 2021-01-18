from django.db import models
from osler.core.validators import validate_name
from osler.core.models import Note, Encounter
import datetime
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _

# Create your models here.


class DrugCategory(models.Model):
    class Meta:
        verbose_name_plural = _("drug categories")
        ordering = ['name', ]

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name


class MeasuringUnit(models.Model):

    class Meta:
        ordering = ['name', ]

    name = models.CharField(max_length=50, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name


class Manufacturer(models.Model):

    class Meta:
        ordering = ['name', ]

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name


class Drug(models.Model):

    class Meta:
        ordering = ['name', ]
        permissions = [
            ('export_csv', _("Can export drug inventory"))
        ]

    name = models.CharField(max_length=100, blank=False, validators=[validate_name])

    unit = models.ForeignKey(MeasuringUnit, on_delete=models.PROTECT, verbose_name=_("unit"))

    dose = models.FloatField(blank=False, null=False, verbose_name=_("dose"))

    stock = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name=_("stock"))

    expiration_date = models.DateField(help_text="MM/DD/YYYY", blank=False,
                                       null=False, verbose_name=_("exspiration date"))

    lot_number = models.CharField(max_length=100, blank=False, verbose_name=_("lot number"))

    category = models.ForeignKey(DrugCategory, on_delete=models.PROTECT, verbose_name=_("category"))

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name=_("manufacturer"))

    history = HistoricalRecords()

    def pre_expire(self):
        today = timezone.now().date()
        two_month = today + datetime.timedelta(days=60)
        return self.expiration_date >= today and self.expiration_date <= two_month

    def expired(self):
        return self.expiration_date < timezone.now().date()

    def can_dispense(self, num):
        return self.stock >= num

    def dispense(self, num):
        self.stock -= num
        self.save()

    def __str__(self):
        return self.name


class DispenseHistory(Note):

    class Meta:
        verbose_name_plural = _("dispense history")
        ordering = ['written_datetime', ]

    dispense = models.PositiveSmallIntegerField(
        blank=False, null=False, verbose_name=_("dispense"))

    drug = models.ForeignKey(
        Drug, on_delete=models.PROTECT, verbose_name=_("drug"))
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE)

    def __str__(self):
        return self.drug.lot_number
