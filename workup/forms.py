from django.forms import fields, ModelForm, CheckboxSelectMultiple, RadioSelect

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field, Button
from crispy_forms.bootstrap import TabHolder, Tab, InlineCheckboxes, \
    AppendedText, PrependedText, FieldWithButtons, StrictButton, InlineRadios, InlineField

from . import models


class WorkupForm(ModelForm):

    temperature_units = fields.ChoiceField(
        label='',
        widget = RadioSelect,
        choices=[('C', 'C'), ('F', 'F')], required=True,
        initial='C')

    class Meta:
        model = models.Workup
        exclude = ['patient', 'clinic_day', 'author', 'signer', 'author_type',
                   'signed_date']
        widgets = {'referral_location': CheckboxSelectMultiple,
                   'referral_type': CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super(WorkupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        js_tab_switch = "$(document).ready(function(){activaTab('TAB-CHANGE');});function activaTab(tab){$('.nav-tabs a[href=\"#' + tab + '\"]').tab('show');};"

        self.helper.layout = Layout(
            TabHolder(
                Tab('Basics',
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
                        Div('t', css_class='col-md-2 col-sm-3 col-xs-6'),
                        Div(InlineRadios('temperature_units'),
                            style='text-align: center;',
                            css_class='col-md-2 col-sm-3 col-xs-6'),
                        Div(AppendedText('bp_sys', 'mmHg'),
                            css_class='col-sm-6 col-xs-12'),
                        Div(AppendedText('bp_dia', 'mmHg'),
                            css_class='col-sm-6 col-xs-12'),
                        title="Vital Signs",
                        css_class="col-xs-12"),
                    Div(
                        Div(AppendedText('height', 'in'),
                            css_class='col-sm-6'),
                        Div(AppendedText('weight', 'kg'),
                            css_class='col-sm-6'),
                        css_class="col-lg-12"), 'pe',
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
        #validating blood pressure
        MAX_SYSTOLIC = 400
        MIN_DIASTOLIC = 40

        if cleaned_data.get('bp_sys') > MAX_SYSTOLIC:
            self.add_error('bp_sys', "Systolic BP is unreasonably high.")

        elif cleaned_data.get('bp_dia') > cleaned_data.get('bp_sys'):
            self.add_error('bp_sys', 'Systolic BP must be higher than diastolic BP.')

        if cleaned_data.get('bp_dia') < MIN_DIASTOLIC:
            self.add_error('bp_dia', 'Diastolic BP is unreasonably low.')

        #validating voucher things
        if cleaned_data.get('got_voucher') and \
           (cleaned_data.get('voucher_amount'))==None:

            self.add_error('voucher_amount', "If the patient recieved a " +
                           "voucher, value of the voucher must be specified.")

        if cleaned_data.get('got_voucher') and \
           (cleaned_data.get('patient_pays'))==None:

            self.add_error('patient_pays', "If the patient recieved a " +
                           "voucher, specify the amount the patient pays.")

        if cleaned_data.get('got_imaging_voucher') and \
            (cleaned_data.get('imaging_voucher_amount'))==None:

            self.add_error('imaging_voucher_amount', "If the patient recieved a " +
                           "imaging voucher, value of the voucher must be specified.")

        if cleaned_data.get('got_imaging_voucher') and \
           (cleaned_data.get('patient_pays_imaging'))==None:

            self.add_error('patient_pays_imaging', "If the patient recieved a " +
                           "imaging voucher, specify the amount the patient pays.")


class ClinicDateForm(ModelForm):
    '''Form for the creation of a clinic date.'''
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']