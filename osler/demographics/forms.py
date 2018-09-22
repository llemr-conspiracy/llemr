from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset

from . import models


class DemographicsForm(ModelForm):

    class Meta:
        model = models.Demographics
        exclude = ['patient', 'creation_date']

    def __init__(self, *args, **kwargs):
        super(DemographicsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
                Fieldset('Medical',
                         'has_insurance',
                         'ER_visit_last_year',
                         'last_date_physician_visit',
                         'chronic_condition'),
                Fieldset('Social',
                         'lives_alone',
                         'dependents',
                         'resource_access',
                         'transportation'),
                Fieldset('Employment',
                         'currently_employed',
                         'education_level',
                         'work_status',
                         'annual_income')
        )

        self.helper.add_input(Submit('submit', 'Submit'))
