'''Forms for the Oser core components.'''
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import (Form, CharField, ModelForm, EmailField,
                          CheckboxSelectMultiple, ModelMultipleChoiceField)
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import InlineCheckboxes

from . import models

# pylint: disable=I0011,E1305


class DuplicatePatientForm(Form):
    first_name = CharField(label='First Name')
    last_name = CharField(label='Last Name')

    def __init__(self, *args, **kwargs):
        super(DuplicatePatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['first_name'].widget.attrs['autofocus'] = True
        self.helper.add_input(Submit('submit', 'Submit'))


class PatientForm(ModelForm):
    class Meta:
        model = models.Patient
        exclude = ['needs_workup', 'demographics']

    # limit the options for the case_managers field to Providers with
    # ProviderType with staff_view=True

    case_managers = ModelMultipleChoiceField(
        required=False,
        queryset=models.Provider.objects.filter(
            clinical_roles__in=models.ProviderType.objects.filter(
                staff_view=True)).distinct().order_by("last_name"),
    )

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.fields['phone'].widget.attrs['autofocus'] = True
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
        exclude = ['associated_user', 'needs_updating']
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


class CrispyAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Login'))
