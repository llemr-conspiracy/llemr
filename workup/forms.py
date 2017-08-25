import decimal

from django.forms import fields, ModelForm, CheckboxSelectMultiple, ModelChoiceField, ModelMultipleChoiceField, RadioSelect

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field, Button
from crispy_forms.bootstrap import (
    TabHolder, Tab, InlineCheckboxes, AppendedText, PrependedText
    )

from pttrack.models import Provider, ProviderType
from . import models


def fahrenheit2centigrade(f):
    """Converts a temperature in fahrenheit to a temperature in
    centigrade. If None, returns None.
    """
    if f is not None:
        return (f - 32) / decimal.Decimal(9.0/5.0)
    else:
        return None

def pounds2kilos(lbs):
    """Converts a weight in pounds to a weight in kilos. If None,
    returns None.
    """

    if lbs is not None:
        return lbs * decimal.Decimal(0.453592)
    else:
        return None

def inches2cm(inches):
    """Converts a length in inches to a length in centimeters. If None,
    returns None.
    """
    if inches is not None:
        return inches * decimal.Decimal(2.54)
    else:
        return None


class WorkupForm(ModelForm):

    temperature_units = fields.ChoiceField(
        label='',
        widget=RadioSelect,
        choices=[('C', 'C'), ('F', 'F')], required=True)

    weight_units = fields.ChoiceField(
        label='',
        widget=RadioSelect,
        choices=[('kg', 'kg'), ('lbs', 'lbs')], required=True)

    height_units = fields.ChoiceField(
        label='',
        widget=RadioSelect,
        choices=[('cm', 'cm'), ('in', 'in')], required=True)


    class Meta:
        model = models.Workup
        exclude = ['patient', 'clinic_day', 'author', 'signer', 'author_type',
                   'signed_date']
        widgets = {'referral_location': CheckboxSelectMultiple,
                   'referral_type': CheckboxSelectMultiple}

    # limit the options for the attending, other_volunteer field to Providers with
    # ProviderType with signs_charts=True, False (includes coordinators and volunteers)
    attending = ModelChoiceField(
        required=False,
        queryset=Provider.objects.filter(
            clinical_roles__in=ProviderType.objects.filter(
                signs_charts=True)).order_by("last_name")
        )

    other_volunteer = ModelMultipleChoiceField(
        required=False,
        queryset=Provider.objects.filter(
            clinical_roles__in=ProviderType.objects.filter(
                signs_charts=False)).distinct().order_by("last_name"),
        )

    def __init__(self, *args, **kwargs):
        super(WorkupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        js_tab_switch = "$(document).ready(function(){activaTab('TAB-CHANGE');});function activaTab(tab){$('.nav-tabs a[href=\"#' + tab + '\"]').tab('show');};"

        self.helper.layout = Layout(
            TabHolder(
                Tab('Basics',
                    'attending',
                    'other_volunteer',
                    'chief_complaint',
                    'diagnosis',
                    InlineCheckboxes('diagnosis_categories'),
                    Button('next', 'Next Section', onclick=js_tab_switch.replace('TAB-CHANGE', 'h-p'))),
                Tab('H & P',
                    'HPI',
                    'PMH_PSH',
                    'fam_hx',
                    'soc_hx',
                    'meds',
                    'allergies',
                    'ros',
                    Button('next', 'Next Section',
                           onclick=js_tab_switch.replace('TAB-CHANGE',
                                                         'physical-exam'))),
                Tab('Physical Exam',
                    Div(
                        Div(AppendedText('hr', 'bpm'),
                            css_class='col-md-4 col-sm-6 col-xs-12'),
                        Div(AppendedText('rr', '/min'),
                            css_class='col-md-4 col-sm-6 col-xs-12'),

                        # Temperature and units
                        Div(AppendedText(
                            't',
                            '''
    <label for="temperature_units">C</label>
    <input name="temperature_units" type="radio" value="C">
    <label for="temperature_units">F</label>
    <input name="temperature_units" type="radio" value="F">
                            '''),
                        css_class='col-md-4 col-sm-6 col-xs-12'
                        ),

                        Div(AppendedText('bp_sys', 'mmHg'),
                            css_class='col-md-4 col-sm-3 col-xs-6'),
                        Div(AppendedText('bp_dia', 'mmHg'),
                            css_class='col-md-4 col-sm-3 col-xs-6'),

                        Div(AppendedText(
                            'height',
                            '''
    <label for="height_units">in</label>
    <input name="height_units" type="radio" value="in">
    <label for="height_units">cm</label>
    <input name="height_units" type="radio" value="cm">
                            '''),
                            css_class='col-md-4 col-sm-6 col-xs-12'),

                        # Weight and units
                        Div(AppendedText(
                                'weight',
                                '''
    <label for="weight_units">kg</label>
    <input name="weight_units" type="radio" value="kg">
    <label for="weight_units">lbs</label>
    <input name="weight_units" type="radio" value="lbs">
                                '''),
                            css_class='col-md-4 col-sm-6 col-xs-12'
                        ),

                        css_class="row"), 'pe',
                    Button('next', 'Next Section', onclick=js_tab_switch.replace('TAB-CHANGE', 'assessment-plan'))),
                Tab('Assessment & Plan',
                    'A_and_P',
                    'rx',
                    Fieldset(
                        'Labs',
                        Div('labs_ordered_internal', css_class='col-lg-6',
                            form_class=''),
                        Div('labs_ordered_quest', css_class='col-lg-6')),
                    Button('next', 'Next Section', onclick=js_tab_switch.replace('TAB-CHANGE', 'referraldischarge'))),
                Tab('Referral/Discharge',
                    Fieldset('Medication Vouchers',
                             'got_voucher',
                             PrependedText('voucher_amount', '$'),
                             PrependedText('patient_pays', '$')),
                    Fieldset('Metro Imaging Vouchers',
                             'got_imaging_voucher',
                             PrependedText('imaging_voucher_amount', '$'),
                             PrependedText('patient_pays_imaging', '$')),
                    Fieldset('Referral',
                             'will_return',
                             Field(
                                 'referral_location',
                                 style="background: #FAFAFA; padding: 10px;"),
                             Field(
                                 'referral_type',
                                 style="background: #FAFAFA; padding: 10px;")),
                    Submit('submit', 'Save', css_class='btn btn-success')
                   )
            )
        )

    def clean(self):
        '''Use form's clean hook to verify that fields in Workup are
        consistent with one another (e.g. if pt recieved a voucher, amount is
        given).'''

        cleaned_data = super(WorkupForm, self).clean()

        if cleaned_data.get('temperature_units') == 'F':
            c = fahrenheit2centigrade(cleaned_data.get('t'))
            cleaned_data['t'] = c

        if cleaned_data.get('weight_units') == 'lbs':
            kgs = pounds2kilos(cleaned_data.get('weight'))
            cleaned_data['weight'] = kgs

        if cleaned_data.get('height_units') == 'in':
            cm = inches2cm(cleaned_data.get('height'))
            cleaned_data['height'] = cm

        if cleaned_data.get('bp_sys') and cleaned_data.get('bp_dia'):
            if cleaned_data.get('bp_sys') <= cleaned_data.get('bp_dia'):
                self.add_error(
                    'bp_sys',
                    'Systolic blood pressure must be strictly greater '
                    'than diastolic blood pressure.')

        #validating voucher things
        if cleaned_data.get('got_voucher') and \
            cleaned_data.get('voucher_amount') is None:

            self.add_error(
                'voucher_amount',
                "If the patient recieved a voucher, value of the "
                "voucher must be specified.")

        if cleaned_data.get('got_voucher') and \
            cleaned_data.get('patient_pays') is None:

            self.add_error(
                'patient_pays',
                "If the patient recieved a voucher, specify the amount "
                "the patient pays.")

        if cleaned_data.get('got_imaging_voucher') and \
            cleaned_data.get('imaging_voucher_amount') is None:

            self.add_error(
                'imaging_voucher_amount',
                "If the patient recieved a imaging voucher, value of "
                "the voucher must be specified.")

        if cleaned_data.get('got_imaging_voucher') and \
            cleaned_data.get('patient_pays_imaging') is None:

            self.add_error(
                'patient_pays_imaging',
                "If the patient recieved a imaging voucher, specify "
                "the amount the patient pays.")


class ClinicDateForm(ModelForm):
    '''Form for the creation of a clinic date.'''
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']