from decimal import Decimal, ROUND_HALF_UP

from django.forms import (
    fields, ModelForm, ModelChoiceField, ModelMultipleChoiceField, RadioSelect
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML
from crispy_forms.layout import Field as CrispyField
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from crispy_forms.utils import TEMPLATE_PACK, render_field

from pttrack.models import Provider, ProviderType
from . import models


def form_required_if(form, conditional, fields):
    """Adds an error to the form if conditional is truthy-false and any
    of fields are None or '' in form's cleaned_data.
    """
    data = form.cleaned_data

    if data.get(conditional):
        for f in fields:
            val = data.get(f)
            if val is None or val == '':
                err_str = ("When %s is specified, %s must also be specified" %
                           (conditional, ", ".join(fields)))
                err_str += (" (%s wasn't)." % f) if len(fields) > 1 else "."

                form.add_error(conditional, err_str)
                [form.add_error(err_fld, err_str) for err_fld in fields]


def form_require_together(form, fields):
    """Adds an error to the form if any of fields are None in form's
    cleaned_data.
    """

    data = form.cleaned_data

    if any(data.get(f) is not None for f in fields):
        for field in fields:
            if data.get(field) is None:
                form.add_error(
                    field,
                    "The fields %s are required together, and %s was "
                    "not provided." % (fields, field))


def fahrenheit2centigrade(f):
    """Converts a temperature in fahrenheit to a temperature in
    centigrade. If None, returns None.
    """
    if f is not None:
        return (f - 32) / Decimal(9.0 / 5.0)
    else:
        return None


def pounds2kilos(lbs):
    """Converts a weight in pounds to a weight in kilos. If None,
    returns None.
    """

    if lbs is not None:
        return lbs * Decimal(0.453592)
    else:
        return None


def inches2cm(inches):
    """Converts a length in inches to a length in centimeters. If None,
    returns None.
    """
    if inches is not None:
        return inches * Decimal(2.54)
    else:
        return None


def unit_selector_html(unit_name, options):
    """Format the units HTML for AppendedText"""

    s = ''

    for option in options:
        s += '''<label for="{name}_units">{option}</label>
                <input name="{name}_units"
                       type="radio" value="{option}">'''.format(
            name=unit_name, option=option)

    return s


class AppendedRadios(CrispyField):
    template = "workup/appended_radios.html"

    def __init__(self, field, radio_field, *args, **kwargs):
        self.field = field
        self.radio_field = radio_field

        self.input_size = None
        css_class = kwargs.get('css_class', '')
        if 'input-lg' in css_class:
            self.input_size = 'input-lg'
        if 'input-sm' in css_class:
            self.input_size = 'input-sm'

        super(AppendedRadios, self).__init__(field, *args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK,
               extra_context=None, **kwargs):
        extra_context = (extra_context.copy() if extra_context is not None
                         else {})
        extra_context.update({
            'radio_field': form[self.radio_field],
            'input_size': self.input_size,
            'active': getattr(self, "active", False)
        })

        if hasattr(self, 'wrapper_class'):
            extra_context['wrapper_class'] = self.wrapper_class
        template = self.get_template_name(template_pack)
        return render_field(
            self.field, form, form_style, context,
            template=template, attrs=self.attrs,
            template_pack=template_pack, extra_context=extra_context, **kwargs
        )


class WorkupForm(ModelForm):

    temperature_units = fields.ChoiceField(
        label='', widget=RadioSelect,
        choices=[('C', 'C',), ('F', 'F')], initial='C', required=False)

    weight_units = fields.ChoiceField(
        label='', widget=RadioSelect,
        choices=[('kg', 'kg'), ('lbs', 'lbs')], required=False)

    height_units = fields.ChoiceField(
        label='', widget=RadioSelect,
        choices=[('cm', 'cm'), ('in', 'in')], required=False)

    class Meta:
        model = models.Workup
        exclude = ['patient', 'author', 'signer', 'author_type',
                   'signed_date', 'referral_location', 'referral_type']

    # limit the options for the attending, other_volunteer field to
    # Providers with ProviderType with signs_charts=True, False
    # (includes coordinators and volunteers)
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

        self.helper.layout = Layout(
            Row(HTML('<h3>Clinical Team</h3>'),
                Div('attending', css_class='col-sm-6'),
                Div('other_volunteer', css_class='col-sm-6'),
                Div('clinic_day', css_class='col-sm-12')
                ),

            Row(HTML('<h3>History</h3>'),
                Div('chief_complaint', css_class='col-sm-6'),
                Div('diagnosis', css_class='col-sm-6'),
                Div(InlineCheckboxes('diagnosis_categories'),
                    css_class='col-xs-12'),
                Div('HPI', css_class='col-xs-12'),
                Div('PMH_PSH', css_class='col-xs-12'),
                Div('fam_hx', css_class='col-md-6'),
                Div('soc_hx', css_class='col-md-6'),
                Div('meds', css_class='col-md-6'),
                Div('allergies', css_class='col-md-6'),
                Div('ros', css_class='col-xs-12')),

            Row(HTML('<h3>Physical Exam</h3>'),
                HTML('<h4>Vital Signs</h4>'),
                Div(AppendedText('hr', 'bpm'),
                    css_class='col-md-4 col-sm-6 col-xs-12'),
                Div(AppendedText('rr', '/min'),
                    css_class='col-md-4 col-sm-6 col-xs-12'),
                Div(AppendedRadios('t', 'temperature_units'),
                    css_class='col-md-4 col-sm-6 col-xs-12'),
                Div(AppendedText('bp_sys', 'mmHg'),
                    css_class='col-md-4 col-sm-3 col-xs-6'),
                Div(AppendedText('bp_dia', 'mmHg'),
                    css_class='col-md-4 col-sm-3 col-xs-6'),
                Div(AppendedRadios('height', 'height_units'),
                    css_class='col-md-4 col-sm-6 col-xs-12'),
                Div(AppendedRadios('weight', 'weight_units'),
                    css_class='col-md-4 col-sm-6 col-xs-12'),
                Div('pe', css_class='col-xs-12')),

            Row(HTML('<h3>Assessment, Plan, & Orders</h3>'),
                Div('A_and_P', css_class='col-xs-12'),
                Div('rx', css_class='col-md-4'),
                Div('labs_ordered_internal', css_class='col-md-4'),
                Div('labs_ordered_quest', css_class='col-md-4'),
                Div(HTML('<h4>Medication Voucher</h4>'),
                    'got_voucher',
                    PrependedText('voucher_amount', '$'),
                    PrependedText('patient_pays', '$'),
                    css_class='col-xs-6',),
                Div(HTML('<h4>Imaging Voucher</h4>'),
                    'got_imaging_voucher',
                    PrependedText('imaging_voucher_amount', '$'),
                    PrependedText('patient_pays_imaging', '$'),
                    css_class='col-xs-6')
                ),

            Submit('submit', 'Save', css_class='btn btn-success')
        )

    def clean(self):
        """Use form's clean hook to verify that fields in Workup are
        consistent with one another (e.g. if pt recieved a voucher, amount is
        given)."""

        cleaned_data = super(WorkupForm, self).clean()

        # we allow specification of units when the measurement is not given
        # because you cannot uncheck radios and the converter methods accept
        # Nones.
        form_required_if(self, 't', ['temperature_units'])
        form_required_if(self, 'height', ['height_units'])
        form_required_if(self, 'weight', ['weight_units'])

        form_required_if(self, 'got_voucher',
                         ['voucher_amount', 'patient_pays'])
        form_required_if(self, 'got_imaging_voucher',
                         ['imaging_voucher_amount',
                          'patient_pays_imaging'])

        if 't' in cleaned_data and cleaned_data.get('t') is not None:
            if cleaned_data.get('temperature_units') == 'F':
                c = Decimal(fahrenheit2centigrade(
                    cleaned_data.get('t'))).quantize(
                        Decimal('.1'), rounding=ROUND_HALF_UP)
                cleaned_data['t'] = c

        if 'weight' in cleaned_data and cleaned_data.get('weight') is not None:
            if cleaned_data.get('weight_units') == 'lbs':
                kgs = Decimal(pounds2kilos(
                    cleaned_data.get('weight'))).quantize(
                        Decimal('.1'), rounding=ROUND_HALF_UP)
                cleaned_data['weight'] = kgs

        if 'height' in cleaned_data and cleaned_data.get('height') is not None:
            if cleaned_data.get('height_units') == 'in':
                cm = int(inches2cm(cleaned_data.get('height')))
                cleaned_data['height'] = cm

        form_require_together(self, ['bp_sys', 'bp_dia'])
        if cleaned_data.get('bp_sys') and cleaned_data.get('bp_dia'):
            if cleaned_data.get('bp_sys') <= cleaned_data.get('bp_dia'):
                for field in ['bp_sys', 'bp_dia']:
                    self.add_error(
                        field,
                        'Systolic blood pressure must be strictly greater '
                        'than diastolic blood pressure.')


class ProgressNoteForm(ModelForm):
    class Meta:
        model = models.ProgressNote
        exclude = ['patient', 'author', 'author_type']

    def __init__(self, *args, **kwargs):
        super(ProgressNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))


class ClinicDateForm(ModelForm):
    '''Form for the creation of a clinic date.'''
    class Meta:
        model = models.ClinicDate
        exclude = ['clinic_date', 'gcal_id']

    def __init__(self, *args, **kwargs):
        super(ClinicDateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.add_input(Submit('submit', 'Submit'))
