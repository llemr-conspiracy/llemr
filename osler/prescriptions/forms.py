from django.forms import (
    fields, formset_factory, ModelForm, ModelChoiceField, ModelMultipleChoiceField, RadioSelect
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML
from crispy_forms.layout import Field as CrispyField
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from crispy_forms.utils import TEMPLATE_PACK, render_field
from osler.prescriptions.models import Prescription


class PrescriptionForm(ModelForm):

    class Meta(object):
        model = Prescription
        fields = ['name','dose','frequency','route']

    def __init__(self, *args, **kwargs):
        super(PrescriptionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(HTML('<h4>Prescripiton</h4>'),
                Div('name',css_class='col-md-3 col-sm-3 col-xs-6'),
                Div('dose', css_class='col-md-3 col-sm-3 col-xs-6'),
                Div('frequency', css_class='col-md-3 col-sm-3 col-xs-6'),
                Div('route', css_class='col-md-3 col-sm-3 col-xs-6'))
        )


PrescriptionFormSet = formset_factory(
    PrescriptionForm,
    extra=4,
)
