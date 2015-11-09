from django.forms import ModelForm

from bootstrap3_datetime.widgets import DateTimePicker
from pttrack.models import Patient

from . import models

class GeneralFollowup(ModelForm):
    '''The form instantiation of a general followup note.'''
    class Meta:
        model = models.GeneralFollowup
        exclude = ['patient', 'author', 'author_type']


class ReferralFollowup(ModelForm):
    '''The form instantiation of a followup for PCP referral.'''

    class Meta:
        model = models.ReferralFollowup
        exclude = ['patient', 'author', 'author_type']

    def clean(self):
        '''ReferralFollowup has some pretty complicated behavior regarding
        which combinations of blank and filled fields are acceptable. We
        implement checks for this here.'''
        cleaned_data = super(ModelForm, self).clean()

        has_appointment = cleaned_data.get("has_appointment")
        contact_resolution = cleaned_data.get("contact_resolution")
        patient_reached = contact_resolution.patient_reached

        if patient_reached:
            if has_appointment:
                # If the patient has an appointment, we require a location and
                # information as to whether or not they showed up.

                if not cleaned_data.get("apt_location"):
                    self.add_error(
                        "apt_location", "Appointment location is required " + 
                        "when the patient has an appointment.")

                if not cleaned_data.get("pt_showed"):
                    self.add_error(
                        "pt_showed", "Please specify whether the patient has" +
                        " gone to their appointment.")

                pt_went = cleaned_data.get("pt_showed")
                if pt_went == "No":
                    if not cleaned_data.get("noshow_reason"):
                        self.add_error(
                            "noshow_reason", "Why didn't the patient go" +
                            "to the appointment?")

                if pt_went == "Yes":
                    if cleaned_data.get('noshow_reason'):
                        self.add_error(
                            "noshow_reason",
                            "If the patient showed, a noshow reason should " +
                            "not be given.")

            else:  # not has_appointment
                if not cleaned_data.get("noapt_reason"):
                    self.add_error(
                        "noapt_reason", "Why didn't the patient make" +
                        "an appointment?")


class VaccineFollowup(ModelForm):
    '''A form to process the handling of a vaccine followup.'''
    class Meta:
        model = models.VaccineFollowup
        exclude = ['patient', 'author', 'author_type']
        widgets = {'dose_date': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                        "pickTime": False})}

    def clean(self):
        '''VaccineFollowups require a next dose date iff there there is a next
        dose.'''

        cleaned_data = super(ModelForm, self).clean()

        if cleaned_data.get('subsq_dose') and \
           not cleaned_data.get('dose_date'):

            self.add_error('dose_date', 'A next dosage date is required if ' +
                           'the patient is returning for another dose.')


class LabFollowup(ModelForm):
    '''The form instantiation of a followup to communicate lab results.'''
    class Meta:
        model = models.LabFollowup
        exclude = ['patient', 'author', 'author_type']


class PatientForm(ModelForm):
    class Meta:
        model = Patient
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

