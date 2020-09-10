from django.db import models
from osler.core.validators import validate_name
from osler.core.models import Note
import datetime
from django.utils import timezone
from simple_history.models import HistoricalRecords

# Create your models here.


class DrugCategory(models.Model):
    class Meta:
        verbose_name_plural = "drug categories"
        ordering = ['name',]

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name


class MeasuringUnit(models.Model):

    class Meta:
        ordering = ['name',]

    name = models.CharField(max_length=50, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name

class Manufacturer(models.Model):

    class Meta:
        ordering = ['name',]

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name

class Drug(models.Model):

    class Meta:
        ordering = ['name',]
        permissions = [
            ('export_csv', "Can export drug inventory")
        ]

    name = models.CharField(max_length=100, blank=False, validators=[validate_name])

    unit = models.ForeignKey(MeasuringUnit, on_delete=models.PROTECT)

    dose = models.FloatField(blank=False, null=False)

    stock = models.PositiveSmallIntegerField(blank=False, null=False)

    expiration_date = models.DateField(help_text="MM/DD/YYYY", blank=False, null=False)

    lot_number = models.CharField(max_length=100, blank=False)

    category = models.ForeignKey(DrugCategory, on_delete=models.PROTECT)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)

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
        verbose_name_plural = "dispense history"
        ordering = ['written_datetime',]

    dispense = models.PositiveSmallIntegerField(blank=False, null=False)

    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)

    def __str__(self):
        return self.drug.lot_number
