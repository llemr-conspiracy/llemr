'''Forms for the SNHC clintools app.'''
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import ModelForm, ValidationError, Form, EmailField

from . import models

# pylint: disable=I0011,E1305

class PatientForm(ModelForm):
    class Meta:
        model = models.Patient
        exclude = ['needs_workup']

    def clean(self):

        cleaned_data = super(ModelForm, self).clean()

        alternate_phone_list = [
            "alternate_phone_1", "alternate_phone_1_owner",
            "alternate_phone_2", "alternate_phone_2_owner",
            "alternate_phone_3", "alternate_phone_3_owner",
            "alternate_phone_4", "alternate_phone_4_owner"]

        for i in [0, 2, 4, 6]:
            j = i+1
            if cleaned_data.get(alternate_phone_list[j]) and \
               not cleaned_data.get(alternate_phone_list[i]):

                self.add_error(
                    alternate_phone_list[j],
                    "An Alternate Phone is required" +
                    " if a Alternate Phone Owner is specified")

            if cleaned_data.get(alternate_phone_list[i]) and \
               not cleaned_data.get(alternate_phone_list[j]):

                self.add_error(
                    alternate_phone_list[i],
                    "An Alternate Phone Owner is required" +
                    " if a Alternate Phone is specified")


class WorkupForm(ModelForm):

    class Meta:
        model = models.Workup
        exclude = ['patient', 'clinic_day', 'author', 'signer', 'author_type',
                   'signed_date']

    def clean(self):
        '''Use form's clean hook to verify that fields in Workup are
        consistent with one another (e.g. if pt recieved a voucher, amount is
        given).'''

        cleaned_data = super(ModelForm, self).clean()

        if cleaned_data.get('got_voucher') and \
           not cleaned_data.get('voucher_amount'):

            self.add_error('voucher_amount', "If the patient recieved a " +
                           "voucher, value of the voucher must be specified.")

        if cleaned_data.get('got_voucher') and \
           not cleaned_data.get('patient_pays'):

            self.add_error('patient_pays', "If the patient recieved a " +
                           "voucher, specify the amount the patient pays.")


class ActionItemForm(ModelForm):
    class Meta:
        model = models.ActionItem
        exclude = ['completion_date', 'author', 'written_date', 'patient',
                   'completion_author', 'author_type']
        widgets = {'due_date': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                       "pickTime": False})}


class ProviderForm(ModelForm):

    provider_email = EmailField(label="Email")

    class Meta:
        model = models.Provider
        exclude = ['associated_user']


class ClinicDateForm(ModelForm):
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']


class DocumentForm(ModelForm):
    class Meta:
        model = models.Document
        exclude = ['patient', 'author', 'author_type']
