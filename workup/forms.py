from django.forms import ModelForm, CheckboxSelectMultiple

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field
from crispy_forms.bootstrap import TabHolder, Tab, InlineCheckboxes, \
    AppendedText, PrependedText

from . import models

class WorkupForm(ModelForm):

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
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basics',
                    'chief_complaint',
                    'diagnosis',
                    InlineCheckboxes('diagnosis_categories')),
                Tab('H & P',
                    'HPI',
                    'PMH_PSH',
                    'fam_hx',
                    'soc_hx',
                    'meds',
                    'allergies',
                    'ros'),
                Tab('Physical Exam',
                    Div(
                        #Div(HTML("<strong>Vital Signs</strong>"),
                        #    css_class='col-lg-1'),
                        Div(AppendedText('hr', 'bpm'), css_class='col-lg-3'),
                        Div(AppendedText('bp', 'mmHg'), css_class='col-lg-3'),
                        Div(AppendedText('rr', '/min'), css_class='col-lg-3'),
                        Div(AppendedText('t', 'C'), css_class='col-lg-3'),
                        title="Vital Signs",
                        css_class="col-lg-12"),
                    Div(
                        Div(AppendedText('height', 'in'), css_class='col-lg-4'),
                        Div(AppendedText('weight', 'kg'), css_class='col-lg-4'),
                        css_class="col-lg-12"),
                    'pe'),
                Tab('Assessment & Plan',
                    'A_and_P',
                    'rx',
                    Fieldset(
                        'Labs',
                        # Div(HTML("<strong>Labs</strong>"),
                        #    css_class='col-lg-1'),
                        Div('labs_ordered_internal', css_class='col-lg-6', form_class=''),
                        Div('labs_ordered_quest', css_class='col-lg-6'))),
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
                   )
            )
        )

        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        '''Use form's clean hook to verify that fields in Workup are
        consistent with one another (e.g. if pt recieved a voucher, amount is
        given).'''

        cleaned_data = super(WorkupForm, self).clean()

        if cleaned_data.get('got_voucher') and \
           not cleaned_data.get('voucher_amount'):

            self.add_error('voucher_amount', "If the patient recieved a " +
                           "voucher, value of the voucher must be specified.")

        if cleaned_data.get('got_voucher') and \
           not cleaned_data.get('patient_pays'):

            self.add_error('patient_pays', "If the patient recieved a " +
                           "voucher, specify the amount the patient pays.")

        if cleaned_data.get('got_imaging_voucher') and \
           not cleaned_data.get('imaging_voucher_amount'):

            self.add_error('imaging_voucher_amount', "If the patient recieved a " +
                           "imaging voucher, value of the voucher must be specified.")

        if cleaned_data.get('got_imaging_voucher') and \
           not cleaned_data.get('patient_pays_imaging'):

            self.add_error('patient_pays_imaging', "If the patient recieved a " +
                           "imaging voucher, specify the amount the patient pays.")


class ClinicDateForm(ModelForm):
    '''Form for the creation of a clinic date.'''
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']