# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.ContinuousMeasurement)
admin.site.register(models.DiscreteMeasurement)
admin.site.register(models.Lab)
admin.site.register(models.LabType)
admin.site.register(models.ContinuousMeasurementType)
admin.site.register(models.DiscreteMeasurementType)
admin.site.register(models.DiscreteResultType)