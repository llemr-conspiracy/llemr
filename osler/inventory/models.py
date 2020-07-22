from django.db import models
from osler.core.validators import validate_name

# Create your models here.


class DrugCategory(models.Model):
    class Meta:
        verbose_name_plural = "drug categories"

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name


class MeasuringUnit(models.Model):

    name = models.CharField(max_length=50, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name

class Manufacturer(models.Model):

    name = models.CharField(max_length=100, primary_key=True, validators=[validate_name])

    def __str__(self):
        return self.name

class Drug(models.Model):

    name = models.CharField(max_length=100, blank=False, validators=[validate_name])

    unit = models.ForeignKey(MeasuringUnit, on_delete=models.PROTECT, blank=True, null=True)

    dose = models.FloatField(blank=True, null=True)

    stock = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True)

    expiration_date = models.DateField(help_text="MM/DD/YYYY", blank=True, null=True)

    lot_number = models.CharField(max_length=100, blank=False)

    category = models.ForeignKey(DrugCategory, on_delete=models.PROTECT)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)

    def can_dispense(self,num):
        if self.stock < num:
            return False
        else:
            return True

    def dispense(self,num):
        self.stock -= num
        self.save()

    def __str__(self):
        return '{}, {}, stock: {}'.format(self.name, self.lot_number, self.stock)

