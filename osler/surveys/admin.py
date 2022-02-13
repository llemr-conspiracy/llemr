from django.contrib import admin
from . import models


class ChoiceInline(admin.TabularInline):
    model = models.Choice


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


admin.site.register(models.Survey)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Choice)
admin.site.register(models.Response)
admin.site.register(models.Answer)
