from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Count, Case, When, Max, Sum, IntegerField
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
                Uninsured=Coalesce(Sum(
                    Case(When(has_insurance=False, then=1),
                         output_field=IntegerField())), 0),
                Insured=Coalesce(Sum(
                    Case(When(has_insurance=True, then=1),
                         output_field=IntegerField())), 0))
        )

        # response.context_data['insurance_responses_total'] = (
        #     response.context_data['has_insurance']['Uninsured'] +
        #     response.context_data['has_insurance']['Insured']
        # )

        response.context_data['currently_employed'] = (
            qs.aggregate(
                Unemployed=Coalesce(Sum(
                    Case(When(currently_employed=False, then=1),
                         output_field=IntegerField())), 0),
                Employed=Coalesce(Sum(
                    Case(When(currently_employed=True, then=1),
                         output_field=IntegerField())), 0)
            )
        )

        # response.context_data['employment_responses_total'] = (
        #     response.context_data['currently_employed']['Unemployed'] +
        #     response.context_data['currently_employed']['Employed']
        # )

        income_ranges = (
            models.IncomeRange.objects
            .annotate(count=Count('demographics'))
        )

        # total_income_responses = (
        #     models.IncomeRange.objects.all()
        #     .aggregate(count=Count('demographics'))
        # )

        most_common_range = (
            income_ranges.aggregate(
                most_common=Max('count')
            )
        )

        response.context_data['income_range_count'] = [
            {'range': x.name,
             'count': x.count,
             'pct': (float(x.count) / float(most_common_range['most_common'])
                     * 100)
             }
            for x in income_ranges
        ]

        education_levels = (
            models.EducationLevel.objects
            .annotate(count=Count('demographics'))
        )
        most_common_level = (
            education_levels.aggregate(
                most_common=Max('count')
            )
        )

        response.context_data['education_levels'] = [
            {'level': x.name,
             'count': x.count,
             'pct': (float(x.count) / float(most_common_level['most_common']) * 100)}
            for x in education_levels
        ]

        chronic_conditions = (
            models.ChronicCondition.objects
            .annotate(count=Count('demographics'))
            .order_by('-count')
        )

        response.context_data['chronic_conditions'] = [
            {'name': x.name,
             'count': x.count}
            for x in chronic_conditions
        ]

        return response



for model in [models.IncomeRange, models.EducationLevel, models.WorkStatus,
              models.ResourceAccess, models.ChronicCondition,
              models.TransportationOption, models.Demographics]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
