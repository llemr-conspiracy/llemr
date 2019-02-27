from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.conf import settings
from pttrack.models import Note

from simple_history.models import HistoricalRecords


class Appointment(Note):

    PSYCH_NIGHT = 'PSYCH_NIGHT'
    ACUTE_FOLLOWUP = 'ACUTE_FOLLOWUP'
    CHRONIC_CARE = 'CHRONIC_CARE'
    VACCINE = 'VACCINE'
    APPOINTMENT_TYPES = (
        (PSYCH_NIGHT, 'Psych Night'),
        (ACUTE_FOLLOWUP, 'Acute Followup'),
        (CHRONIC_CARE, 'Chronic Care'),
        (VACCINE, "Vaccine Followup")
    )

    clindate = models.DateField(verbose_name="Appointment Date")
    clintime = models.TimeField(
        verbose_name="Time of Appointment",
        default=now().replace(
            hour=settings.OSLER_DEFAULT_APPOINTMENT_HOUR,
            minute=0,
            second=0,
            microsecond=0))
    appointment_type = models.CharField(
        max_length=15, choices=APPOINTMENT_TYPES,
        verbose_name='Appointment Type', default=CHRONIC_CARE)
    comment = models.TextField(
        help_text="What should happen at this appointment?")
    history = HistoricalRecords()

    def clean(self):
        ids = Appointment.objects.filter(clindate=self.clindate).\
            values_list('id', flat=True)

        if (ids.count() >= settings.OSLER_MAX_APPOINTMENTS and
                self.id not in ids):
            raise ValidationError(
                "Osler is configured only to allow %s appointments per day" %
                settings.OSLER_MAX_APPOINTMENTS)
