'''Forms for the Oser core components.'''

from django.forms import (
    Form, CharField, ModelForm, EmailField, CheckboxSelectMultiple,
    ModelMultipleChoiceField, CheckboxInput)
from django.contrib.auth.forms import AuthenticationForm

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes

from osler.core import models
from osler.users.models import User

from django.utils.translation import gettext_lazy as _


class CustomCheckbox(Field):
    template = 'core/custom_checkbox.html'

# pylint: disable=I0011,E1305


class DuplicatePatientForm(Form):
    first_name = CharField(label=_('First Name'))
    last_name = CharField(label=_('Last Name'))

    def __init__(self, *args, **kwargs):
        super(DuplicatePatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['first_name'].widget.attrs['autofocus'] = True
        self.helper.add_input(Submit('submit', _('Submit')))


class PatientForm(ModelForm):
    class Meta(object):
        model = models.Patient
        exclude = ['demographics']
        if not settings.OSLER_DISPLAY_CASE_MANAGERS:
            exclude.append('case_managers')

    if settings.OSLER_DISPLAY_CASE_MANAGERS:
        case_managers = ModelMultipleChoiceField(
            required=False,
            queryset=get_user_model().objects
                .filter(groups__permissions__codename='case_manage_Patient')
                .distinct()
                .order_by("last_name")
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
        self.helper.add_input(Submit('submit', _('Submit')))
        self.fields['address'].widget.attrs = {'placeholder': settings.OSLER_DEFAULT_ADDRESS}

    def clean(self):

        cleaned_data = super(ModelForm, self).clean()

        N_ALTS = 5

        alt_phones = ["alternate_phone_" + str(i) for i in range(1, N_ALTS)]
        alt_owners = [phone + "_owner" for phone in alt_phones]

        for (alt_phone, alt_owner) in zip(alt_phones, alt_owners):

            if cleaned_data.get(alt_owner) and not cleaned_data.get(alt_phone):
                self.add_error(
                    alt_phone,
                    _("An Alternate Phone is required if a Alternate Phone Owner is specified"))

            if cleaned_data.get(alt_phone) and not cleaned_data.get(alt_owner):
                self.add_error(
                    alt_owner,
                    _("An Alternate Phone Owner is required if a Alternate Phone is specified"))


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
<<<<<<< HEAD
        self.helper.add_input(Submit('submit', _('Submit')))


class CrispyAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', _('Login')))
=======
        self.helper.add_input(Submit('submit', 'Submit'))

>>>>>>> master
