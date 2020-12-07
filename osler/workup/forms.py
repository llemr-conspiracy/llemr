from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import (
    fields, ModelForm, ModelChoiceField, ModelMultipleChoiceField, RadioSelect
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML
from crispy_forms.layout import Field as CrispyField
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from crispy_forms.utils import TEMPLATE_PACK, render_field

from osler.workup import models
from osler.core.models import Encounter

from past.utils import old_div

from django.utils.translation import gettext_lazy as _


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
        return old_div((f - 32), Decimal(9.0 / 5.0))
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

    class Meta(object):
        model = models.Workup
        exclude = ['patient', 'author', 'signer', 'author_type',
                   'signed_date', 'referral_location', 'referral_type']

    # limit the options for the attending, other_volunteer field by
    # checking the signs charts permission.
    can_sign_perm_codename = 'sign_Workup'
    attending = ModelChoiceField(
        required=False,
        queryset=get_user_model().objects.filter(
            groups__in=Group.objects.filter(
            permissions__codename=can_sign_perm_codename)
        ).distinct()
    )

    other_volunteer = ModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.all()
    )

    encounter = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(WorkupForm, self).__init__(*args, **kwargs)
        pt = kwargs.pop('pt')

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.fields['encounter'].queryset = Encounter.objects\
            .filter(patient=pt).order_by('clinic_day')

        self.helper.layout = Layout(
            Row(HTML('<h3>Clinical Team</h3>'),
                Div('attending', css_class='col-sm-6'),
                Div('other_volunteer', css_class='col-sm-6'),
                Div('encounter', css_class='col-sm-12')
                ),

            Row(HTML('<h3>History</h3>'),
                Div('chief_complaint', css_class='col-sm-6'),
                Div('diagnosis', css_class='col-sm-6'),
                Div(InlineCheckboxes('diagnosis_categories'),
                    css_class='col-sm-12'),
                Div('hpi', css_class='col-xs-12'),
                Div('pmh', css_class='col-md-6'),
                Div('psh', css_class='col-md-6'),
                Div('fam_hx', css_class='col-md-6'),
                Div('soc_hx', css_class='col-md-6'),
                Div('meds', css_class='col-md-6'),
                Div('allergies', css_class='col-md-6'),
                Div('ros', css_class='col-xs-12')),

            Row(HTML('<h3>Physical Exam</h3>'),
                HTML('<h4>Vital Signs</h4>'),
                Div(AppendedText('bp_sys', 'mmHg'),
                    css_class='col-md-3 col-sm-3 col-xs-6'),
                Div(AppendedText('bp_dia', 'mmHg'),
                    css_class='col-md-3 col-sm-3 col-xs-6'),
                Div(AppendedText('hr', 'bpm'),
                    css_class='col-md-3 col-sm-3 col-xs-6'),
                Div(AppendedText('rr', '/min'),
                    css_class='col-md-3 col-sm-3 col-xs-6')),

            Row(Div(AppendedRadios('t', 'temperature_units'),
                    css_class='col-md-3 col-sm-3 col-xs-6'),
                Div(AppendedRadios('weight', 'weight_units'),
                    css_class='col-md-3 col-sm-4 col-xs-6'),
                Div(AppendedRadios('height', 'height_units'),
                    css_class='col-md-3 col-sm-4 col-xs-6'),
                Div('pe', css_class='col-xs-12')),

            Row(HTML('<h3>Assessment, Plan, & Orders</h3>'),
                Div('a_and_p', css_class='col-xs-12'),
                Div('rx', css_class='col-md-4'),
                Div('labs_ordered_internal', css_class='col-md-4'),
                Div('labs_ordered_external', css_class='col-md-4')
            ),

            Row(
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

            Submit('pending', 'Save for Later', css_class='btn btn-warning'),
            Submit('complete', 'Submit', css_class='btn btn-success')
        )

        self.fields['ros'].widget.attrs['rows'] = 15
        self.fields['pe'].widget.attrs['rows'] = 14

        if not settings.OSLER_DISPLAY_DIAGNOSIS:
            # delete diagnosis
            self.helper.layout[1].pop(2)
            # delete diagnosis category
            self.helper.layout[1].pop(2)

        if not settings.OSLER_DISPLAY_VOUCHERS:
            # delete medication voucher
            self.helper.layout[5].pop()
            # # delete imaging voucher
            self.helper.layout[5].pop()
            

    def clean(self):
        """Use form's clean hook to verify that fields in Workup are
        consistent with one another (e.g. if pt recieved a voucher, amount is
        given)."""

        cleaned_data = super(WorkupForm, self).clean()

        if 'pending' in self.data:
            cleaned_data['is_pending'] = True
            return

        required_fields = [
            'chief_complaint', 
            'hpi', 
            'pmh',
            'psh',
            'meds',
            'allergies',
            'fam_hx',
            'soc_hx',
            'ros',
            'pe',
            'a_and_p'
            ]
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, _("This field is required."))

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

        attending = cleaned_data.get('attending')
        if attending and attending in cleaned_data.get('other_volunteer'):
            self.add_error('other_volunteer', 
            'Attending physician must be different from other volunteers.')
        
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

        for field in ['ros', 'pe'] + settings.OSLER_WORKUP_COPY_FORWARD_FIELDS:
            user_input = cleaned_data.get(field)
            if not user_input:
                continue
            cleaned_data[field] = user_input.strip()
            if "UPDATE" in cleaned_data.get(field):
                self.add_error(field, _("Please delete the heading and update contents as necessary"))
        
        form_require_together(self, ['bp_sys', 'bp_dia'])
        if cleaned_data.get('bp_sys') and cleaned_data.get('bp_dia'):
            if cleaned_data.get('bp_sys') <= cleaned_data.get('bp_dia'):
                for field in ['bp_sys', 'bp_dia']:
                    self.add_error(
                        field,
                        'Systolic blood pressure must be strictly greater '
                        'than diastolic blood pressure.')


class AttestableBasicNoteForm(ModelForm):
    class Meta(object):
        model = models.AttestableBasicNote
        fields = ['title', 'text']

    encounter = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        pt = kwargs.pop('pt')
        super(AttestableBasicNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['encounter'].queryset = Encounter.objects\
            .filter(patient=pt).order_by('clinic_day')
        self.helper.add_input(Submit('submit', 'Submit'))


class BasicNoteForm(ModelForm):
    class Meta(object):
        model = models.BasicNote
        fields = ['title', 'text']

    encounter = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        pt = kwargs.pop('pt')
        super(BasicNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['encounter'].queryset = Encounter.objects\
            .filter(patient=pt).order_by('clinic_day')
        self.helper.add_input(Submit('submit', 'Submit'))


class AddendumForm(ModelForm):
    class Meta(object):
        model = models.Addendum
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super(AddendumForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))

