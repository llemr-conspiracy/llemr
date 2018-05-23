from django.db import models
from django.utils.timezone import now
from pttrack.models import Note
# from workup.models import ClinicDate
from simple_history.models import HistoricalRecords
from datetime import datetime, time


# From StackOverflow (https://stackoverflow.com/questions/16027516/can-i-set-a-specific-default-time-for-a-django-datetime-field/16049125)
# def default_start_time():
#     now = datetime.now()
#     start = now.replace(hour=9, minute=0, second=0, microsecond=0)
#     return start if start > now else start + timedelta(days=7)  



class Appointment(Note):

    PSYCH_NIGHT = 'PSYCH_NIGHT'
    ACUTE_FOLLOWUP = 'ACUTE_FOLLOWUP'
    CHRONIC_CARE = 'CHRONIC_CARE'
    APPOINTMENT_TYPES = (
        (PSYCH_NIGHT, 'Psych Night'),
        (ACUTE_FOLLOWUP, 'Acute Followup'),
        (CHRONIC_CARE, 'Chronic Care')
    )

    clindate = models.DateField(verbose_name="Appointment Date")
    clintime = models.TimeField(verbose_name="Time of Appointment", default=time(9,0))
    appointmentType = models.CharField(max_length=15, choices=APPOINTMENT_TYPES,
                                       verbose_name='Appointment Type',
                                       default=CHRONIC_CARE)
    comment = models.TextField(
        help_text="What should happen at this appointment?")
    history = HistoricalRecords()
