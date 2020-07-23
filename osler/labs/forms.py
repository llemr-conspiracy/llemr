from django.forms import (
	fields, ModelForm, ModelChoiceField, ModelMultipleChoiceField, DecimalField, RadioSelect,Form
)
from django.shortcuts import render, redirect, get_object_or_404
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from django.urls import reverse
from . import models
from django.db.models import DateTimeField, ForeignKey
import django.db
import decimal


# Create a lab object to a patient without any measurements 
class LabCreationForm(ModelForm):
	class Meta:
		model = models.Lab
		exclude = ['patient','written_datetime']

	def __init__(self, *args, **kwargs):
		patient_obj = kwargs.pop('pt')
		patient_name = patient_obj.name()
		super(LabCreationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		
		self.helper.layout = Layout(
			Row(
				HTML('<p>Patient name: <b>%s</b> </p>' %patient_name),
				Div('lab_type', css_class='col-sm-6')),

			Submit('choose-lab', 'Choose Lab', css_class='btn btn-success')
		)


# Fill in corresponding measurements in a lab object
class MeasurementsCreationForm(Form):
	def __init__(self, *args, **kwargs):
		self.qs_fields = kwargs.pop('qs_mt')
		self.new_lab_type = kwargs.pop('new_lab_type')
		self.pt = kwargs.pop('pt')

		super(MeasurementsCreationForm, self).__init__(*args, **kwargs)

		pt_info = Row(
				HTML('<p>Patient name: <b>%s</b> </p>' %self.pt.name()),
				HTML('<p>Lab type: <b>%s</b> </p>' %self.new_lab_type))

		self.fields_display = [pt_info]
		for measurement_type in self.qs_fields:
			str_name = measurement_type.short_name
			unit = measurement_type.unit
			self.fields_display.append(Field(str_name))
			self.fields_display[-1] = AppendedText(str_name,unit)

			value_qs=models.DiscreteResultType.objects.filter(measurement_type=measurement_type)
			if len(value_qs)==0: 
				self.fields[str_name] = DecimalField()
			else:
				self.fields[str_name]= ModelChoiceField(queryset=value_qs)


		self.helper = FormHelper()
		self.helper.form_method = 'post'

		if len(self.fields_display)==0:
			button = []
		else:
			button = [Submit('save-lab', 'Save Lab', css_class='btn btn-success')]

		self.helper.layout = Layout(
			*(self.fields_display + button)
			)

	def save(self):
		self.new_lab = models.Lab.objects.create(
			patient = self.pt,
			lab_type = self.new_lab_type
			)
		for field in self.qs_fields:
			if type(self.cleaned_data[field.short_name])==decimal.Decimal:
				models.ContinuousMeasurement.objects.create(
					measurement_type = field,
					lab = self.new_lab,
					value = self.cleaned_data[field.short_name]
				)
			else:
				models.DiscreteMeasurement.objects.create(
					measurement_type = field,
					lab = self.new_lab,
					value = self.cleaned_data[field.short_name]
				)
		#print(self.new_lab.get_day())
		return self.new_lab
