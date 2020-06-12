from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VaccineConfig(AppConfig):
    name = "osler.vaccine"
    verbose_name = _("Vaccine")