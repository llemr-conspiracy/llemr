from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.conf import settings

from simple_history.models import HistoricalRecords

from osler.core.models import Note

from django.utils.translation import gettext_lazy as _

def generate_default_appointment_time():
    return now().replace(
        hour=settings.OSLER_DEFAULT_APPOINTMENT_HOUR,
        minute=0,
        second=0,
        microsecond=0)


class Appointment(Note):

    class Meta:
        ordering = ["-clindate", "-clintime"]

    PSYCH_NIGHT = 'PSYCH_NIGHT'
    ACUTE_FOLLOWUP = 'ACUTE_FOLLOWUP'
    CHRONIC_CARE = 'CHRONIC_CARE'
    VACCINE = 'VACCINE'
    APPOINTMENT_TYPES = (
        (PSYCH_NIGHT, _('Psych Night')),
        (ACUTE_FOLLOWUP, _('Acute Followup')),
        (CHRONIC_CARE, _('Chronic Care')),
        (VACCINE, _('Vaccine Followup'))
    )

    clindate = models.DateField(verbose_name=_("Appointment Date"))
    clintime = models.TimeField(
        verbose_name=_("Time of Appointment"),
        default=generate_default_appointment_time)
    appointment_type = models.CharField(
        max_length=15, choices=APPOINTMENT_TYPES,
        verbose_name=_('Appointment Type'), default=CHRONIC_CARE)
    comment = models.TextField(
        help_text=_("What should happen at this appointment?"))

    pt_showed = models.NullBooleanField(
        verbose_name=_("Patient Showed"),
        blank=True, help_text=_("Did the patient come to this appointment?"))

    history = HistoricalRecords()
    
    def __str__(self):
        return _("Appointment ({type}) for {name} on {date}").format(
            type=self.verbose_appointment_type(),
            name=self.patient.name(),
            date=str(self.clindate))

    def verbose_appointment_type(self):
        appointment_type_index = list(zip(*self.APPOINTMENT_TYPES))[0].index(
            self.appointment_type)

        return self.APPOINTMENT_TYPES[appointment_type_index][1]

    def clean(self):
        ids = Appointment.objects.filter(clindate=self.clindate).\
            values_list('id', flat=True)

        if (ids.count() >= settings.OSLER_MAX_APPOINTMENTS and
                self.id not in ids):
            raise ValidationError(
                _("Osler is configured only to allow %s appointments per day") %
                settings.OSLER_MAX_APPOINTMENTS)
