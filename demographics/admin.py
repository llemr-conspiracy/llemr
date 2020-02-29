from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Count, Case, When, Value, Sum, IntegerField
from django.db.models.functions import Coalesce
from . import models

@admin.register(models.DemographicsSummary)
class DemographicsSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/demographics_summary_change_list.html'

    def changelist_view(self, request, extra_context=None):
        response = super(DemographicsSummaryAdmin, self).changelist_view(
            request, extra_context)

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        response.context_data['has_insurance'] = (
            qs.aggregate(
                uninsured=Coalesce(Sum(
                    Case(When(has_insurance=False, then=1),
                         output_field=IntegerField())), 0),
                insured=Coalesce(Sum(
                    Case(When(has_insurance=True, then=1),
                         output_field=IntegerField())), 0))
        )

        response.context_data['insurance_responses_total'] = (
            response.context_data['has_insurance']['uninsured'] +
            response.context_data['has_insurance']['insured']
        )

        response.context_data['currently_employed'] = (
            qs.aggregate(
                unemployed=Coalesce(Sum(
                    Case(When(currently_employed=False, then=1),
                         output_field=IntegerField())), 0),
                employed=Coalesce(Sum(
                    Case(When(currently_employed=True, then=1),
                         output_field=IntegerField())), 0)
            )
        )

        response.context_data['employment_responses_total'] = (
            response.context_data['currently_employed']['unemployed'] +
            response.context_data['currently_employed']['employed']

        )

        return response



for model in [models.IncomeRange, models.EducationLevel, models.WorkStatus,
              models.ResourceAccess, models.ChronicCondition,
              models.TransportationOption, models.Demographics]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
