from django.forms import (fields, ModelForm, Form, ModelChoiceField)
from django.forms.models import model_to_dict, fields_for_model

from django.forms.widgets import SplitDateTimeWidget
from django.contrib.admin.widgets import AdminDateWidget

from django.shortcuts import get_object_or_404
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (AppendedText)

from . import models
from . import utils
from osler.core.models import Encounter

from itertools import chain

# Create a lab object to a patient without any measurements 
class LabCreationForm(ModelForm):
    class Meta:
        model = models.Lab
        fields = ['lab_type']
        exclude = ['patient', 'lab_time']

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

    encounter=ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.new_lab_type = kwargs.pop('new_lab_type')
        self.pt = kwargs.pop('pt')
        self.lab_pk = kwargs.pop('lab_pk') if ('lab_pk' in kwargs) else None
        
        super(MeasurementsCreationForm, self).__init__(*args, **kwargs)

        STYLE = 'width:400px;'

        pt_info = Row(
                HTML('<p>Patient name: <b>%s</b> </p>' %self.pt.name()),
                HTML('<p>Lab type: <b>%s</b> </p>' %self.new_lab_type))
        self.fields_display = [pt_info]

        self.fields['encounter'].queryset = Encounter.objects\
            .filter(patient=self.pt).order_by('clinic_day')
        self.fields['encounter'] = fields_for_model(models.Lab)['encounter']
        self.fields['encounter'].widget.attrs['style'] = 'width: 600px'
        self.fields_display.append(Field('encounter'))

        self.fields['lab_time'] = fields_for_model(models.Lab)['lab_time']
        self.fields['lab_time'].widget.attrs['style'] = STYLE
        self.fields_display.append(Field('lab_time'))
        if self.lab_pk is not None:
            self.fields['lab_time'].initial = models.Lab.objects.get(pk=self.lab_pk).lab_time
            self.fields['encounter'].initial = models.Lab.objects.get(pk=self.lab_pk).encounter

        self.measurements_list = []
        if self.lab_pk is not None:
            self.measurements_list = utils.get_measurements_from_lab(self.lab_pk)

        self.measurementtypes_list = utils.get_measurementtypes_from_labtype(self.new_lab_type.id)

        for measurement_type in self.measurementtypes_list:
            str_name = measurement_type.short_name
            unit = measurement_type.get_unit()
            value_type = measurement_type.get_value_type()
            self.fields_display.append(Div(AppendedText(str_name,unit),style=STYLE))
            
            if value_type=='Continuous': 
                new_field = fields_for_model(models.ContinuousMeasurement)['value']
            elif value_type=='Discrete': 
                new_field = fields_for_model(models.DiscreteMeasurement)['value']
                new_field.queryset = models.DiscreteResultType.objects.filter(measurement_type=measurement_type)
            new_field.label = str_name
            new_field.widget.attrs['style'] = STYLE
            if self.lab_pk is not None:
                try:
                    #new_field.initial = self.measurements_list.get(measurement_type=measurement_type).value
                    new_field.initial = next((mt.value for mt in self.measurements_list if mt.measurement_type == measurement_type), None)
                except:
                    pass

            self.fields[str_name] = new_field

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        if len(self.fields_display)==0:
            button = []
        else:
            button = [Submit('save-lab', 'Save Lab', css_class='btn btn-success')]

        self.helper.layout = Layout(
            *(self.fields_display + button)
            )


    def save(self, *args, **kwargs):
        self.lab_pk = kwargs.pop('lab_pk') if ('lab_pk' in kwargs) else None

        # Creating a new lab
        if self.lab_pk is None:
            self.new_lab = models.Lab.objects.create(
                patient = self.pt,
                lab_type = self.new_lab_type,
                lab_time = self.cleaned_data['lab_time'],
                encounter = self.cleaned_data['encounter']
                )

            for mt in self.measurementtypes_list:
                if mt.get_value_type()=='Continuous':
                    models.ContinuousMeasurement.objects.create(
                        measurement_type = mt,
                        lab = self.new_lab,
                        value = self.cleaned_data[mt.short_name]
                    )
                elif mt.get_value_type()=='Discrete':
                    models.DiscreteMeasurement.objects.create(
                        measurement_type = mt,
                        lab = self.new_lab,
                        value = self.cleaned_data[mt.short_name]
                    )

        # Updating an existing lab
        else:
            self.new_lab = get_object_or_404(models.Lab, pk=self.lab_pk)
            if self.cleaned_data['lab_time']!=self.new_lab.lab_time:
                self.new_lab.lab_time = self.cleaned_data['lab_time']
                self.new_lab.save()
            measurement_list = self.measurements_list
            for measure in measurement_list:
                field_name = measure.measurement_type.short_name
                if self.cleaned_data[field_name]!=measure.value:
                    measure.value = self.cleaned_data[field_name]
                    measure.save()
        return self.new_lab
