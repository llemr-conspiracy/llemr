from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from . import models

# Register your models here.
for model in [models.Appointment]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
