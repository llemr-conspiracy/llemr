'''Forms for the Oser core components.'''
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import ModelForm, EmailField, CheckboxSelectMultiple

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field
from crispy_forms.bootstrap import TabHolder, Tab, InlineCheckboxes, \
    AppendedText, PrependedText

from . import models

# pylint: disable=I0011,E1305

class PatientForm(ModelForm):
    class Meta:
        model = models.Patient
        exclude = ['needs_workup', 'demographics']

    
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper['languages'].wrap(InlineCheckboxes)
        self.helper['ethnicities'].wrap(InlineCheckboxes)
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):

        cleaned_data = super(ModelForm, self).clean()

        N_ALTS = 5

        alt_phones = ["alternate_phone_" + str(i) for i in range(1, N_ALTS)]
        alt_owners = [phone + "_owner" for phone in alt_phones]

        for (alt_phone, alt_owner) in zip(alt_phones, alt_owners):

            if cleaned_data.get(alt_owner) and not cleaned_data.get(alt_phone):
                self.add_error(
                    alt_phone,
                    "An Alternate Phone is required" +
                    " if a Alternate Phone Owner is specified")

            if cleaned_data.get(alt_phone) and not cleaned_data.get(alt_owner):
                self.add_error(
                    alt_owner,
                    "An Alternate Phone Owner is required" +
                    " if a Alternate Phone is specified")


class ActionItemForm(ModelForm):
    class Meta:
        model = models.ActionItem
        exclude = ['completion_date', 'author', 'written_date', 'patient',
                   'completion_author', 'author_type']
        widgets = {'due_date': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                       "pickTime": False})}

    def __init__(self, *args, **kwargs):
        super(ActionItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))

class ProviderForm(ModelForm):

    provider_email = EmailField(label="Email")

    class Meta:
        model = models.Provider
        exclude = ['associated_user']
        widgets = {'referral_location': CheckboxSelectMultiple,
                   'referral_type': CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper['languages'].wrap(InlineCheckboxes)
        self.helper['clinical_roles'].wrap(InlineCheckboxes)
        self.helper.add_input(Submit('submit', 'Submit'))

class DocumentForm(ModelForm):
    class Meta:
        model = models.Document
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))