from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DemographicsConfig(AppConfig):
    name = "osler.demographics"
    verbose_name = _("Demographics")
