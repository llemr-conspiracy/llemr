from django.forms import ModelForm

from bootstrap3_datetime.widgets import DateTimePicker

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from . import models

class GeneralFollowup(ModelForm):
    '''The form instantiation of a general followup note.'''
    class Meta:
        model = models.GeneralFollowup
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('followup_close', 'Submit and Close Action'))
        self.helper.add_input(Submit('followup_create', 'Submit and Create Action'))
        super(GeneralFollowup, self).__init__(*args, **kwargs)


class ReferralFollowup(ModelForm):
    '''The form instantiation of a followup for PCP referral.'''

    class Meta:
        model = models.ReferralFollowup
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.add_input(Submit('followup_close', 'Submit and Close Action'))
        self.helper.add_input(Submit('followup_create', 'Submit and Create Action'))
        super(ReferralFollowup, self).__init__(*args, **kwargs)

    def clean(self):
        '''ReferralFollowup has some pretty complicated behavior regarding
        which combinations of blank and filled fields are acceptable. We
        implement checks for this here.'''
        cleaned_data = super(ReferralFollowup, self).clean()

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
        else:
            detail_params = ["noshow_reason", "noapt_reason", "pt_showed"]

            for param in detail_params:
                if cleaned_data.get(param):
                    self.add_error(
                        param,
                        "You can't give a " + param.replace("_", " ") +
                        " value if contact was unsuccessful")


class VaccineFollowup(ModelForm):
    '''A form to process the handling of a vaccine followup.'''
    class Meta:
        model = models.VaccineFollowup
        exclude = ['patient', 'author', 'author_type']
        widgets = {'dose_date': DateTimePicker(options={"format": "YYYY-MM-DD",
 
                                                        "pickTime": False})}

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('followup_close', 'Submit and Close Action'))
        self.helper.add_input(Submit('followup_create', 'Submit and Create Action'))
        super(VaccineFollowup, self).__init__(*args, **kwargs)

    def clean(self):
        '''VaccineFollowups require a next dose date iff there there is a next
        dose.'''

        cleaned_data = super(VaccineFollowup, self).clean()

        if cleaned_data.get('subsq_dose') and \
           not cleaned_data.get('dose_date'):

            self.add_error('dose_date', 'A next dosage date is required if ' +
                           'the patient is returning for another dose.')


class LabFollowup(ModelForm):
    '''The form instantiation of a followup to communicate lab results.'''
    class Meta:
        model = models.LabFollowup
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('followup_close', 'Submit and Close Action'))
        self.helper.add_input(Submit('followup_create', 'Submit and Create Action'))
        super(LabFollowup, self).__init__(*args, **kwargs)
