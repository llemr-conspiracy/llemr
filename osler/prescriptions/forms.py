from django.forms import (
    fields, inlineformset_factory, ModelForm, ModelChoiceField, ModelMultipleChoiceField, RadioSelect
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML
from crispy_forms.layout import Field as CrispyField
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from crispy_forms.utils import TEMPLATE_PACK, render_field
from osler.prescriptions.models import Prescription
from osler.inventory.models import Drug

from django.forms import ChoiceField

class PrescriptionForm(ModelForm):

    drug = ModelChoiceField(queryset=Drug.objects.all())

    class Meta(object):
        model = Prescription
        fields = ['dose','frequency','route']


PrescriptionFormSet = inlineformset_factory(
    Drug, Prescription, form=PrescriptionForm,
    fields=['drug','dose','frequency','route'], extra=2, can_delete=True
)
