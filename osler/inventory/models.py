from django.db import models

# Create your models here.


class DrugCategory(models.Model):
    class Meta:
        verbose_name_plural = "drug categories"

    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class MeasuringUnit(models.Model):

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):

    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

class Drug(models.Model):

    name = models.CharField(max_length=100, blank=False)

    unit = models.ForeignKey(MeasuringUnit, on_delete=models.PROTECT, blank=True, null=True)

    dose = models.FloatField(blank=True, null=True)

    stock = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True)

    expiration_date = models.DateField(help_text="MM/DD/YYYY", blank=True, null=True)

    lot_number = models.CharField(max_length=100, blank=True)

    category = models.ForeignKey(DrugCategory, on_delete=models.PROTECT)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

