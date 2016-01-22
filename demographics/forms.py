from django.forms import ModelForm


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field
from crispy_forms.bootstrap import TabHolder, Tab

from . import models

class DemographicsForm(ModelForm):

    class Meta:
        model = models.Demographics
        exclude = ['patient', 'creation_date']

    def __init__(self, *args, **kwargs):
        super(DemographicsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Medical',
                    'has_insurance',
                    'ER_visit_last_year',
                    'last_date_physician_visit',
                    'chronic_condition'),
                Tab('Social',
                    'lives_alone',
                    'dependents',
                    'transportation'),
                Tab('Employment',
                	'education_level',
                	'currently_employed',
                	'work_status',
                	'annual_income',
                	)
                )
        )

        self.helper.add_input(Submit('submit', 'Submit'))
                    