from __future__ import unicode_literals
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from crispy_forms.bootstrap import InlineCheckboxes


from . import models

from django.utils.translation import gettext_lazy as _

class DemographicsForm(ModelForm):

    class Meta:
        model = models.Demographics
        exclude = ['patient', 'creation_date']

    def __init__(self, *args, **kwargs):
        super(DemographicsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
                Fieldset(_('Medical'),
                         'has_insurance',
                         'ER_visit_last_year',
                         'last_date_physician_visit',
                         'chronic_condition'),
                Fieldset(_('Social'),
                         'lives_alone',
                         'dependents',
                         'resource_access',
                         'transportation'),
                Fieldset(_('Employment'),
                         'currently_employed',
                         'education_level',
                         'work_status',
                         'annual_income')
        )
        self.helper['chronic_conditions'].wrap(InlineCheckboxes)
        self.helper['resource_access'].wrap(InlineCheckboxes)


        self.helper.add_input(Submit('submit', _('Submit')))
