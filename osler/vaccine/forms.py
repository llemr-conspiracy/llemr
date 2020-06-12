from django.forms import (ModelForm, ModelChoiceField)
from django import forms
from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from osler.vaccine import models
# from osler.core.forms import ActionItemForm
# from osler.followup.forms import BaseFollowup


class VaccineSeriesForm(ModelForm):
    class Meta(object):
        model = models.VaccineSeries
        fields = ['kind']

    def __init__(self, *args, **kwargs):
        super(VaccineSeriesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['kind'].queryset = models.VaccineSeriesType.objects.all()
        self.helper.add_input(Submit('submit', 'Create vaccine series'))


class VaccineDoseForm(ModelForm):
    class Meta(object):
        model = models.VaccineDose
        fields = ['which_dose']

    def __init__(self, series_type, *args, **kwargs):
        super(VaccineDoseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['which_dose'].queryset = models.VaccineDoseType.objects.filter(kind=series_type)
        self.helper.add_input(Submit('submit', 'Log vaccine dose'))


class VaccineSeriesSelectForm(forms.Form):
    series = ModelChoiceField(queryset=None)

    def __init__(self, pt_id, *args, **kwargs):
        super(VaccineSeriesSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.fields['series'].queryset = models.VaccineSeries.objects\
            .filter(patient_id=pt_id)

        self.helper.add_input(Submit('submit', 'Submit'))


# class VaccineActionItemForm(ActionItemForm):
# 	class Meta(object):
#         model = models.VaccineActionItem
#         exclude = ['completion_date', 'author', 'written_date', 'patient',
#                    'completion_author', 'author_type','vaccine']


# class VaccineFollowup(BaseFollowup):
#     '''A form to process the handling of a vaccine followup.'''
#     class Meta(object):
#         model = models.VaccineFollowup
#         exclude = ['patient', 'author', 'author_type']

#     def clean(self):
#         '''VaccineFollowups require a next dose date iff there there is a next
#         dose.'''

#         cleaned_data = super(VaccineFollowup, self).clean()

#         if cleaned_data.get('subsq_dose') and \
#            not cleaned_data.get('dose_date'):

#             self.add_error('dose_date', 'A next dosage date is required if ' +
#                            'the patient is returning for another dose.')
        
