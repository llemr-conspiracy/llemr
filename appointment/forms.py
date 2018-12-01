from django.forms import ModelForm, TimeInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from bootstrap3_datetime.widgets import DateTimePicker

from .models import Appointment


class AppointmentForm(ModelForm):

    class Meta:
        model = Appointment
        exclude = ['author', 'author_type']
        widgets = {'clindate': DateTimePicker(options={"format": "MM/DD/YYYY"}),
                   'clintime': TimeInput(format='%H:%M')}

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
