from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LabsConfig(AppConfig):
    name = "osler.labs"
    verbose_name = _("Labs")
