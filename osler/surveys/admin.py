from django.contrib import admin
from . import models

# Template
admin.site.register(models.Survey)
admin.site.register(models.Question)
admin.site.register(models.Choice)
admin.site.register(models.Response)
admin.site.register(models.Answer)
