from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DatadashboardConfig(AppConfig):
    name = 'osler.datadashboard'
    verbose_name = _("Data_Dashboard")
