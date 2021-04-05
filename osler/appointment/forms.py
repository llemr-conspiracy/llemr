from __future__ import unicode_literals
from builtins import object
from django.forms import ModelForm, TimeInput, TextInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Appointment

from django.utils.translation import gettext_lazy as _

class AppointmentForm(ModelForm):

    class Meta(object):
        model = Appointment
        fields = ['clindate', 'clintime', 'appointment_type', 'comment',
                  'patient']

        widgets = {
            'clindate': TextInput(attrs={'type': 'date'}),
            'clintime': TimeInput(format='%H:%M', attrs={'type': 'time'})
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', _('Submit')))
