'''Forms for the Oser core components.'''
from django.forms import (
    Form, CharField, ModelForm, EmailField, CheckboxSelectMultiple,
    ModelMultipleChoiceField, CheckboxInput, TextInput
)

from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes

from osler.core import models
from osler.users.models import User

from django.utils.translation import gettext_lazy as _


class CustomCheckbox(Field):
    template = 'core/custom_checkbox.html'


class DuplicatePatientForm(Form):
    first_name = CharField(label=_('First Name'))
    last_name = CharField(label=_('Last Name'))

    def __init__(self, *args, **kwargs):
        super(DuplicatePatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['first_name'].widget.attrs['autofocus'] = True
        self.helper.add_input(Submit('submit', _('Submit')))


class PatientPhoneNumberForm(ModelForm):

    class Meta:
        model = models.PatientPhoneNumber
        fields = ['phone_number', 'description', 'patient']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['patient'].widget = HiddenInput()

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.add_input(Submit('submit', 'Submit'))


class PatientForm(ModelForm):
    class Meta(object):
        model = models.Patient
        exclude = (
            ['demographics', 'phone'] +
            [f'alternate_phone_{i}' for i in range(1,5)] +
            [f'alternate_phone_{i}_owner' for i in range(1,5)]
        )
        if not settings.OSLER_DISPLAY_CASE_MANAGERS:
            exclude.append('case_managers')
        widgets = {
            'date_of_birth': TextInput(attrs={'type': 'date'}),
        }

    if settings.OSLER_DISPLAY_CASE_MANAGERS:
        case_managers = ModelMultipleChoiceField(
            required=False,
            queryset=get_user_model().objects
            .filter(groups__permissions__codename='case_manage_Patient')
            .distinct()
            .order_by("last_name")
        )

    phone = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget,
        required=False
    )

    description = CharField(
        label='Phone Label',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.fields['middle_name'].widget.attrs['autofocus'] = True
        self.helper['languages'].wrap(InlineCheckboxes)
        self.helper['ethnicities'].wrap(InlineCheckboxes)
        self.helper.add_input(Submit('submit', _('Submit')))
        self.fields['address'].widget.attrs = {'placeholder': settings.OSLER_DEFAULT_ADDRESS}


    def clean(self):

        cleaned_data = super(ModelForm, self).clean()

        if cleaned_data.get('description') and not cleaned_data.get('phone'):
            self.add_error(
                description,
                _("Phone number is required if a description is provided.")
            )


class AbstractActionItemForm(ModelForm):
    '''The base class for action item forms'''
    class Meta(object):
        abstract = True
        model = models.AbstractActionItem
        exclude = []

    def __init__(self, *args, **kwargs):
        super(AbstractActionItemForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.fields['instruction'].queryset = models.ActionInstruction\
            .objects.filter(active=True)
        self.helper.add_input(Submit('submit', _('Submit')))


class ActionItemForm(AbstractActionItemForm):
    class Meta(object):
        model = models.ActionItem
        exclude = ['completion_date', 'author', 'written_date', 'patient',
                   'completion_author', 'author_type']
        widgets = {'priority': CheckboxInput}
        # widgets = {'due_date': DateTimePicker(options={"format": "MM/DD/YYYY"})}


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
        widgets = {'phone': PhoneNumberInternationalFallbackWidget}

    def __init__(self, *args, **kwargs):
        super(UserInitForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper['languages'].wrap(InlineCheckboxes)
        self.helper['groups'].wrap(InlineCheckboxes)
        self.helper.add_input(Submit('submit', _('Submit')))

        required_fields = [
            'first_name',
            'last_name',
            'groups'
        ]
        for field in required_fields:
            self.fields[field].required = True

        self.fields['groups'].help_text = ""


class DocumentForm(ModelForm):
    class Meta(object):
        model = models.Document
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
