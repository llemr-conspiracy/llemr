'''Forms for the Oser core components.'''

from django.forms import (Form, CharField, ModelForm, EmailField,
                          CheckboxSelectMultiple, ModelMultipleChoiceField)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes

from . import models
from osler.users.models import User


class CustomCheckbox(Field):
    template = 'core/custom_checkbox.html'

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
    class Meta(object):
        model = models.Patient
        exclude = ['needs_workup', 'demographics']

    # limit the options for the case_managers
    case_managers = ModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects
        .filter(groups__permissions__codename='can_case_manage_Patient')
        .distinct()
        .order_by("last_name"),
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
    class Meta(object):
        model = models.ActionItem
        exclude = ['completion_date', 'author', 'written_date', 'patient',
                   'completion_author', 'author_type']
        # widgets = {'due_date': DateTimePicker(options={"format": "MM/DD/YYYY"})}

    def __init__(self, *args, **kwargs):

        super(ActionItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Row(
                Column(css_class='form-group col-md-3 col-xs-4'),
                Column('due_date', css_class='form-group col-md-3 col-xs-4'),
                Column('instruction', css_class='form-group col-md-3 col-xs-4'),
                css_class='form-row'
            ),
            Row(
                Column(css_class='form-group col-md-3 col-xs-4'),
                Column('comments', css_class='form-group col-md-6 col-xs-6')
            ),
            CustomCheckbox('priority'),
            Row(
                Column(Submit('submit', 'Submit'),
                    css_class='formgroup col-md-offset-3 col-xs-offset-4')
            )
        )

        self.fields['instruction'].queryset = models.ActionInstruction\
            .objects.filter(active=True)


class UserInitForm(ModelForm):

    class Meta(object):
        model = User
        fields = [
            'name',
            'first_name', 
            'last_name', 
            'phone', 
            'languages', 
            'gender', 
            'groups'
        ]

    def __init__(self, *args, **kwargs):
        super(UserInitForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper['languages'].wrap(InlineCheckboxes)
        self.helper['groups'].wrap(InlineCheckboxes)
        self.helper.add_input(Submit('submit', 'Submit'))

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['groups'].required = True
        self.fields['groups'].help_text = ""


class DocumentForm(ModelForm):
    class Meta(object):
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
