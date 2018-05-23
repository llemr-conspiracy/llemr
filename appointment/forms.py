from django.forms import ModelForm
from .models import Appointment

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.widgets import TimeInput

from .models import Appointment


class AppointmentForm(ModelForm):

    class Meta:
        model = Appointment
        exclude = ['author', 'author_type']
        widgets = {'clindate': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                       "pickTime": False}),
                   'clintime': TimeInput(format='%H:%M')}

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        cleaned_data = super(ModelForm, self).clean()
        date = cleaned_data.get("clindate")

        if date:
            # Only check number of appointments if valid so far
            number_of_appointments = Appointment.objects.filter(clindate=date).count()
            if number_of_appointments >= 5:
                self.add_error('clindate', 'There cannot be more than 5' +
                               ' appointments per day. Please pick a different date')

