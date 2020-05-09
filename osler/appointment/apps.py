from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppointmentConfig(AppConfig):
    name = "osler.appointment"
    verbose_name = _("Appointment")
