from __future__ import unicode_literals
from builtins import object
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from . import models

from django.utils.translation import gettext_lazy as _

class BaseFollowup(ModelForm):
    '''The base class for followup forms'''
    class Meta(object):
        abstract = True
        model = models.Followup
        exclude = []

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('followup_close', _('Submit and Close Action'), css_class = 'btn btn-warning'))
        self.helper.add_input(Submit('followup_create', _('Submit and Create Action'), css_class = 'btn btn-info'))
        super(BaseFollowup, self).__init__(*args, **kwargs)


class VaccineFollowup(BaseFollowup):
    '''A form to process the handling of a vaccine followup.'''
    class Meta(object):
        model = models.VaccineFollowup
        exclude = ['patient', 'author', 'author_type']

    def clean(self):
        '''VaccineFollowups require a next dose date iff there there is a next
        dose.'''

        cleaned_data = super(VaccineFollowup, self).clean()

        if cleaned_data.get('subsq_dose') and \
           not cleaned_data.get('dose_date'):

            self.add_error('dose_date', _('A next dosage date is required if the patient is returning for another dose.'))


class ActionItemFollowup(BaseFollowup):
    class Meta(object):
        model = models.ActionItemFollowup
        exclude = ['patient', 'author', 'author_type','action_item']


class LabFollowup(BaseFollowup):
    '''The form instantiation of a followup to communicate lab results.'''
    class Meta(object):
        model = models.LabFollowup
        exclude = ['patient', 'author', 'author_type']
