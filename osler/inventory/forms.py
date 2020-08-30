from . import models
from django.forms import ModelForm, Form, ModelChoiceField
import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from osler.core import models as core_models

class DrugForm(ModelForm):
    class Meta:
        model = models.Drug
        fields = ['name', 'category', 'stock', 'manufacturer', 'lot_number', 'unit', 'dose', 'expiration_date']

    def __init__(self, *args, **kwargs):
        super(DrugForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Submit'))

class DuplicateDrugForm(ModelForm):
    class Meta:
        model = models.Drug
        fields = ['name', 'lot_number', 'manufacturer']

    def __init__(self, *args, **kwargs):
        super(DuplicateDrugForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['name'].widget.attrs['autofocus'] = True
        self.helper.add_input(Submit('submit', 'Submit'))

class SelectPatientForm(Form):
    patient = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(SelectPatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['patient'].queryset = core_models.Patient.objects.all() \
                                                                    .order_by('last_name') \
                                                                    .select_related('gender')

        self.helper.add_input(Submit('submit', 'Select Patient'))

class DispenseDrugForm(ModelForm):
    class Meta(object):
        model = models.DispenseHistory
        fields = ['dispense']

    def __init__(self, pk, *args, **kwargs):
        super(DispenseDrugForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['dispense'].widget.attrs['min'] = 1
        self.fields['dispense'].widget.attrs['max'] = models.Drug.objects.get(pk=pk).stock
        self.helper.add_input(Submit('submit', 'Dispense'))
