from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkupConfig(AppConfig):
    name = "osler.workup"
    verbose_name = _("Workup")
