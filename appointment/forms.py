from __future__ import unicode_literals
from builtins import object
from django.forms import ModelForm, TimeInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Appointment


class AppointmentForm(ModelForm):

    class Meta(object):
        model = Appointment
        fields = ['clindate', 'clintime', 'appointment_type', 'comment',
                  'patient']

        widgets = {
            # 'clindate': DateTimePicker(options={"format": "YYYY-MM-DD"}),
            'clintime': TimeInput(format='%H:%M')
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
