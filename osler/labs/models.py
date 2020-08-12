import datetime

from django.db import models
from django.utils import timezone
from osler.core.models import (Patient)

# type of lab panels
# e.g. BMP, A1c, CBC, etc.
class LabType(models.Model):
	name = models.CharField(max_length=30)
	order_index = models.PositiveIntegerField(default=0, blank=False, null=False)

	class Meta:
		ordering = ['order_index']
		
	def __str__(self):
		return self.name


# object of a lab panel
class Lab(models.Model):
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	
	#written_datetime = models.DateTimeField(auto_now_add=True)

	lab_time = models.DateTimeField(default=timezone.now)

	lab_type = models.ForeignKey(LabType, on_delete=models.PROTECT)

	class Meta:
		ordering = ['-lab_time']

	def __str__(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.lab_time.astimezone(to_tz).strftime("%B-%d-%Y, %H:%M")
		return '%s | %s | %s ' %(str(self.patient),str(self.lab_type),str_time)

	def get_day(self):
		to_tz = timezone.get_default_timezone()
		day = self.lab_time.astimezone(to_tz).date()
		return day

	def get_table_time(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.lab_time.astimezone(to_tz).strftime("%m/%d/%Y\n%H%M")
		return str_time

	def get_table_day(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.lab_time.astimezone(to_tz).strftime("%m/%d/%Y")
		return str_time


# type of measurements in a lab panel
# e.g. Na+, K+ in BMP, A1c in A1c, WBC in CBC, etc.
class MeasurementType(models.Model):
	long_name = models.CharField(max_length=30, primary_key=True,
		help_text="A unique name of the measurement")
	short_name = models.CharField(max_length=30)

	VALUE_TYPE_CHOICES = (
		('Continuous','Numerical'),
		('Discrete','Categorical')
	)
	value_type = models.CharField(max_length=15, choices=VALUE_TYPE_CHOICES)

	unit = models.CharField(max_length=15, blank=True, null=True,
		help_text="Leave blank if this measurement is categorical")
	panic_upper = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True,
		help_text="All labs above this value will display as red with a warning sign. Will also be used as the upper bound of reference. Leave blank if this measurement is categorical")
	panic_lower = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True,
		help_text="All labs below this value will display as blue with a warning sign. Will also be used as the lower bound of reference. Leave blank if this measurement is categorical")

	lab_type = models.ForeignKey(LabType, on_delete=models.PROTECT)

	order_index = models.PositiveIntegerField(default=0, blank=False, null=False,
		help_text="Order at which this measurement will display")


	class Meta:
		ordering = ['order_index']

	def __lt__(self, other):
		return ((self.order_index) < (other.order_index))

	def __str__(self):
		return self.long_name

	def panic(self, value):
		if self.value_type=='Continuous':
			if ((self.panic_lower!=None) and (value < self.panic_lower)):
				return True
			elif((self.panic_upper!=None) and (value > self.panic_upper)):
				return True
			return False
		elif self.value_type=='Discrete':
			# Only give warnings if the option is part of this measurement type
			if not DiscreteResultType.objects.filter(measurement_type=self, name=value.name).exists():
				return False
			if value.is_panic == 'T':
				return True
			elif value.is_panic == 'F':
				return False
			return False

	def panic_color(self, value):
		if self.value_type=='Continuous':
			if ((self.panic_lower!=None) and (value < self.panic_lower)):
				return '#0000FF' #blue
			elif((self.panic_upper!=None) and (value > self.panic_upper)):
				return '#f00' #red
			return ''
		elif self.value_type=='Discrete':
			if value.is_panic == 'T':
				return '#f00' #red
			elif value.is_panic == 'F':
				return ''
			return ''


	def get_ref(self):
		if self.value_type == 'Discrete':
			return ''
		if (self.panic_lower==None and self.panic_upper==None):
			return ''
		else:
			lower_str = '' if (self.panic_lower is None) else ('%2g' %self.panic_lower)
			upper_str = '' if (self.panic_upper is None) else ('%2g' %self.panic_upper)
			unit_str = '' if (self.unit is None) else str(self.unit)
			return '[%s - %s %s]' %(lower_str, upper_str, unit_str)
	## def get_field()


# parent class of measurements

## make this a abstract class (e.g. note)
class Measurement(models.Model):
	measurement_type = models.ForeignKey(MeasurementType, on_delete=models.PROTECT)
	lab = models.ForeignKey(Lab, on_delete=models.CASCADE)


# object of a continuous measurement
class ContinuousMeasurement(Measurement):
	#class Meta:
	#	app_label = 'osler.labs'
	value = models.DecimalField(max_digits=5, decimal_places=1)

	def __str__(self):
		return '%s: %2g' %(self.measurement_type, self.value)


# type of discrete results
# e.g. Positive, Negative, Trace, etc.
class DiscreteResultType(models.Model):
	name = models.CharField(max_length=30, primary_key=True)
	measurement_type = models.ManyToManyField(MeasurementType)
	PANIC_CHOICES = (
		('T','Abnormal value'),
		('F','Normal value')
	)
	is_panic = models.CharField(max_length=1, choices=PANIC_CHOICES,
		default='T',
		help_text="If abnormal, all labs with this value will display as red with a warning sign.")
	#measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


# object of a continuous measurement
class DiscreteMeasurement(Measurement):
	value = models.ForeignKey(DiscreteResultType, on_delete=models.PROTECT)

	def __str__(self):
		value_name = DiscreteResultType.objects.get(pk=self.value)
		return '%s: %s' %(self.measurement_type, value_name.name)
