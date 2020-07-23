# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from osler.core.models import (Patient)

# type of lab panels
# e.g. BMP, A1c, CBC, etc.
class LabType(models.Model):
	name = models.CharField(max_length=30)

	class Meta:
		app_label = 'osler.labs'
		
	def __str__(self):
		return self.name


# object of a lab panel
class Lab(models.Model):
	class Meta:
		app_label = 'osler.labs'

	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	
	written_datetime = models.DateTimeField(auto_now_add=True)

	lab_type = models.ForeignKey(LabType, on_delete=models.PROTECT)

	def __unicode__(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.written_datetime.astimezone(to_tz).strftime("%B-%d-%Y, %H:%M")
		return '%s | %s | %s ' %(str(self.patient),str(self.lab_type),str_time)

	def get_day(self):
		day = self.written_datetime.date()
		return day

	def get_table_time(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.written_datetime.astimezone(to_tz).strftime("%m/%d/%Y\n%H%M")
		return str_time

	def get_table_day(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.written_datetime.astimezone(to_tz).strftime("%m/%d/%Y")
		return str_time


# type of measurements in a lab panel
# e.g. Na+, K+ in BMP, A1c in A1c, WBC in CBC, etc.
class MeasurementType(models.Model):
	class Meta:
		app_label = 'osler.labs'

	long_name = models.CharField(max_length=30, primary_key=True)
	short_name = models.CharField(max_length=15)
	unit = models.CharField(max_length=15, blank=True, null=True)
	panic_upper = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	panic_lower = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

	lab_type = models.ForeignKey(LabType, on_delete=models.PROTECT)

	def __unicode__(self):
		return self.long_name

	def panic(self, value):
		if value < self.panic_lower:
			return '⚠'
		elif value > self.panic_upper:
			return '⚠⚠'
		return ''

	## def get_field()


# parent class of measurements

## make this a abstract class (e.g. note)
class Measurement(models.Model):
	class Meta:
		app_label = 'osler.labs'

	measurement_type = models.ForeignKey(MeasurementType, on_delete=models.PROTECT)
	lab = models.ForeignKey(Lab, on_delete=models.CASCADE)


# object of a continuous measurement
class ContinuousMeasurement(Measurement):
	class Meta:
		app_label = 'osler.labs'
	value = models.DecimalField(max_digits=5, decimal_places=1)

	def __unicode__(self):
		return '%s: %2g' %(self.measurement_type, self.value)


# type of discrete results
# e.g. Positive, Negative, Trace, etc.
class DiscreteResultType(models.Model):
	class Meta:
		app_label = 'osler.labs'

	name = models.CharField(max_length=30, primary_key=True)
	#measurement_type = models.ManyToManyField(MeasurementType)
	measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


# object of a continuous measurement
class DiscreteMeasurement(Measurement):
	class Meta:
		app_label = 'osler.labs'

	value = models.ForeignKey(DiscreteResultType, on_delete=models.PROTECT)
	## panic 

	def __unicode__(self):
		value_name = DiscreteResultType.objects.get(pk=self.value)
		return '%s: %s' %(self.measurement_type, value_name.name)
