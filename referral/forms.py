from __future__ import print_function

from django.forms import ModelForm
from django import forms
from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from bootstrap3_datetime.widgets import DateTimePicker

class ReferralForm(ModelForm):
    class Meta:
        model = models.Referral
        fields = ['location', 'comments']

    def __init__(self, referral_location_qs, *args, **kwargs):
        super(ReferralForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['location'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['location'].queryset = referral_location_qs
        self.helper.add_input(Submit('submit', 'Create referral'))

class FollowupRequestForm(ModelForm):
    class Meta:
        model = models.FollowupRequest
        fields = ['due_date', 'contact_instructions']
        widgets = {'due_date': DateTimePicker(options={"format": "MM/DD/YYYY"})}

    def __init__(self, *args, **kwargs):
        super(FollowupRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))

class PatientContactForm(ModelForm):

    SUCCESSFUL_REFERRAL = 'successful-referral'
    REQUEST_FOLLOWUP = 'request-new-followup'
    UNSUCCESSFUL_REFERRAL = 'give-up'

    class Meta:
        model = models.PatientContact
        fields = ['contact_method', 'contact_status',
                  'has_appointment', 'no_apt_reason',
                  'appointment_location', 'pt_showed',
                  'no_show_reason']
        widgets = {
            'appointment_location': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        referral_location_qs = kwargs.pop('referral_location_qs', None)
        super(PatientContactForm, self).__init__(*args, **kwargs)
        if referral_location_qs is not None:
            self.fields['appointment_location'].queryset = referral_location_qs

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.add_input(Submit(self.SUCCESSFUL_REFERRAL,
                                     'Save successful referral'))
        self.helper.add_input(Submit(self.REQUEST_FOLLOWUP,
                                     'Save unsuccessful referral and request followup'))
        self.helper.add_input(Submit(self.UNSUCCESSFUL_REFERRAL,
                                     'Save unsuccessful referral'))

    def clean(self):
        '''Form has some complicated logic around which parts of the form can
        be left blank and which ones must be filled out.
        We check for a valid form submission here.'''

        cleaned_data = super(PatientContactForm, self).clean()

        has_appointment = cleaned_data.get("has_appointment")
        contact_status = cleaned_data.get("contact_status")

        # If the user has not provided a contact status, break out to trigger
        # only the first two incompletion errors (first two fields -- has
        # appointment and contact status are required)
        if contact_status is None:
            return

        patient_reached = contact_status.patient_reached

        if patient_reached:
            if has_appointment == models.PatientContact.PTSHOW_YES:
                # Require user to specify if patient showed up for appointment
                # if that patient made an appointment
                if not cleaned_data.get("pt_showed"):
                    self.add_error(
                        "pt_showed", "Please specify whether the patient has"
                        " gone to their appointment.")

                if not cleaned_data.get("appointment_location"):
                    self.add_error(
                        "appointment_location", "Please specify which "
                        "provider the patient contacted.")

                if cleaned_data.get("no_apt_reason"):
                    self.add_error(
                        "no_apt_reason",
                        "If the patient has an appointment, a no "
                        "appointment reason should not be given")

                pt_went = cleaned_data.get("pt_showed")
                if pt_went == models.PatientContact.PTSHOW_NO:
                    if not cleaned_data.get("no_show_reason"):
                        self.add_error(
                            "no_show_reason", "Why didn't the patient go "
                            "to the appointment?")
                # if pt_went == models.PatientContact.PTSHOW_YES
                else:
                    if cleaned_data.get('no_show_reason'):
                        self.add_error(
                            "no_show_reason",
                            "If the patient showed, a no show reason should "
                            "not be given.")

            elif has_appointment == models.PatientContact.PTSHOW_NO:
                # Require user to specify why the patient did not make
                # an appointment
                if not cleaned_data.get("no_apt_reason"):
                    self.add_error(
                        "no_apt_reason", "Why didn't the patient make "
                        "an appointment?")

                if cleaned_data.get("appointment_location"):
                    self.add_error(
                        "appointment_location", "Cannot speicfy "
                        "a location if patient has not made appointment.")

                pt_went = cleaned_data.get("pt_showed")
                if pt_went == models.PatientContact.PTSHOW_YES:
                    self.add_error(
                        "pt_showed", "Patient could not have "
                        "attended appointment without scheduling one.")

                if cleaned_data.get("no_show_reason"):
                    self.add_error(
                        "no_show_reason", "Cannot specify no show "
                        "reason if patient has not made appointment.")

            else:
                if not cleaned_data.get("has_appointment"):
                    self.add_error(
                        "has_appointment", "Need to specify if patient " +
                        "has appointment")

        # if patient has not been reached
        else:
            # If user did not make contact with the patient all other
            # parts of the form should be left blank
            detail_params = {
                "no_show_reason": "no show reason",
                "no_apt_reason": "no appointment reason",
                "appointment_location": "appointment location",
                "pt_showed": "patient showed",
                "has_appointment": "has appointment"}

            for param, param_verbose in detail_params.iteritems():
                if cleaned_data.get(param):
                    self.add_error(
                        param,
                        "You can't give a " + param_verbose +
                        " value if contact was unsuccessful")

        # Each submission button has specific rules for which fields can be selected
        # For example, for a referral to be successful, the pt_went must be true
        pt_went = cleaned_data.get("pt_showed")
        if self.SUCCESSFUL_REFERRAL in self.data:
            if pt_went != models.PatientContact.PTSHOW_YES:
                self.add_error(
                    "pt_showed", "Cannot submit a successful " +
                    "referral if the patient did not show up for" +
                    " an appointment")

        # Verify that give up is only selected if the patient has not
        # completed a referral
        if self.REQUEST_FOLLOWUP in self.data:
            if pt_went == models.PatientContact.PTSHOW_YES:
                self.add_error(
                    "pt_showed", "Cannot give up on a " +
                    "successful referral")

        # Verify that give up is only selected if the patient has not
        # completed a referral
        if self.UNSUCCESSFUL_REFERRAL in self.data:
            if pt_went == models.PatientContact.PTSHOW_YES:
                self.add_error(
                    "pt_showed", "Cannot request a new referral " +
                    "follow up on a successful referral")


class ReferralSelectForm(forms.Form):
    referrals = forms.ModelChoiceField(queryset=None)

    def __init__(self, pt_id, *args, **kwargs):
        super(ReferralSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['referrals'].queryset = models.Referral.objects.filter(
            patient_id=pt_id,
            status=models.Referral.STATUS_PENDING,
            followuprequest__in=models.FollowupRequest.objects.all())
        self.helper.add_input(Submit('submit', 'Submit'))
