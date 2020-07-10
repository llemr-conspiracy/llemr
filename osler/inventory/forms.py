from django import forms
from django.forms import ModelForm, Form
from . import models

from django.forms import (Form, CharField, ModelForm, EmailField,
                          CheckboxSelectMultiple, ModelMultipleChoiceField, IntegerField)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.layout import ButtonHolder, Submit

from crispy_forms.layout import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


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
    #name = CharField(label='Drug Name')
    #lot_number= CharField(label='Lot Number', required=True)

    def __init__(self, *args, **kwargs):
        super(DuplicateDrugForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['name'].widget.attrs['autofocus'] = True
        self.helper.add_input(Submit('submit', 'Submit'))
