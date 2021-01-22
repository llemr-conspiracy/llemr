from __future__ import unicode_literals
from builtins import str
from functools import partial

import django.utils.timezone
from django.db.models import Min

from osler import workup,referral
from osler.core import models

from osler.core.api import serializers

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet


class PatientViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = serializers.PatientSerializer
    queryset = models.Patient.objects

    def get_queryset(self):
        '''
        Restricts returned patients according to query params
        '''

        filter_funcs = {
            None: lambda x: x,
            'active': active_patients_filter,
            'ai_active': active_ai_patients_filter,
            'ai_inactive': inactive_ai_patients_filter,
            'unsigned_workup': unsigned_workup_patients_filter,
            'user_cases': partial(user_cases, self.request.user),
            'ai_priority': priority_ai_patients_filter
        }

        # This doesn't sort by latest time, just latest date
        def by_latest_key(pt):
            latest_wu = pt.latest_workup()
            if latest_wu is None:
                latest_date = pt.history.last().history_date.date()
            else:
                latest_date = latest_wu.encounter.clinic_day
            return latest_date

        queryset = models.Patient.objects
        sort = self.request.query_params.get('sort', None)
        filter_name = self.request.query_params.get('filter', None)

        if sort is not None:
            if str(sort) == 'latest_workup':
                pt_list_latest = list(models.Patient.objects.all())
                pt_list_latest.sort(key=by_latest_key, reverse=True)
                queryset = pt_list_latest
            else:
                queryset = queryset.order_by(sort)

        queryset = filter_funcs[filter_name](queryset) \
            .select_related('gender') \
            .prefetch_related('workup_set') \
            .prefetch_related('actionitem_set') \
            .prefetch_related('followuprequest_set') \
            .prefetch_related('vaccineactionitem_set')

        return queryset

   
def active_patients_filter(qs):
    '''Filter a queryset of patients for those that are listed as
    active. This is used to display a subset of patients for voluneers
    giving care on a particular clinic day (to hide the giant list of
    pts).
    '''

    return qs.filter(encounter__status__is_active=True)


def merge_pt_querysets_by_soonest_date(qs1, qs2):
    '''Utility function to merge two patient querysets by the
    soonest due date. Called by active_ai_patients_filter and
    inactive_ai_patients_filter. Requires that inputs both
    have soonest_due_date annotated.
    '''

    patient_dict = {p: p.soonest_due_date for p in qs1}

    for p in qs2:
        if p not in patient_dict:
            patient_dict[p] = p.soonest_due_date
        else:
            patient_dict[p] = min(patient_dict[p], p.soonest_due_date)

    out_list = [t[0] for t in sorted(
        [(p, soonest_due_date) for p, soonest_due_date
         in list(patient_dict.items())],
        key=lambda x: x[1])
    ]

    return out_list


def active_ai_patients_filter(qs):
    '''Filter a queryset of patients for those that have overdue action
    items.
    '''

    ai_qs = models.ActionItem.objects \
        .filter(due_date__lte=django.utils.timezone.now().date()) \
        .filter(completion_date=None) \
        .select_related('patient')

    pts_with_active_ais = models.Patient.objects \
        .filter(actionitem__in=ai_qs) \
        .distinct().annotate(soonest_due_date=Min('actionitem__due_date'))

    referral_qs = referral.models.FollowupRequest.objects \
        .filter(due_date__lte=django.utils.timezone.now().date()) \
        .filter(completion_date=None) \
        .select_related('patient')

    pts_with_active_referral_models = models.Patient.objects \
        .filter(followuprequest__in=referral_qs) \
        .distinct().annotate(soonest_due_date=Min('followuprequest__due_date'))

    out_list = merge_pt_querysets_by_soonest_date(
        pts_with_active_ais, pts_with_active_referral_models)

    return out_list


def inactive_ai_patients_filter(qs):
    '''Build a queryset of patients for those that have active action
    items due in the future.
    '''

    future_ai_pts = models.Patient.objects.filter(
        actionitem__in=models.ActionItem.objects
            .filter(due_date__gt=django.utils.timezone.now().date())
            .filter(completion_date=None)
            .select_related('patient')
    ).annotate(soonest_due_date=Min('actionitem__due_date'))

    future_referral_pts = models.Patient.objects.filter(
        followuprequest__in=referral.models.FollowupRequest.objects
            .filter(due_date__gt=django.utils.timezone.now().date())
            .filter(completion_date=None)
            .select_related('patient')
    ).annotate(soonest_due_date=Min('followuprequest__due_date'))

    out_list = merge_pt_querysets_by_soonest_date(
        future_ai_pts, future_referral_pts)

    return out_list


def unsigned_workup_patients_filter(qs):
    '''Build a queryset that returs a list of patients with an unsigned
    workup.
    '''

    wu_qs = workup.models.Workup.objects \
        .filter(signer__isnull=True) \
        .order_by('last_name') \
        .select_related('patient')  # optimization only

    return models.Patient.objects.filter(workup__in=wu_qs)


def priority_ai_patients_filter(qs):
    '''Build a queryset that returs a list of patients with a high priority
    action item.
    '''

    priority_ai_pts = models.Patient.objects.filter(
        actionitem__in=models.ActionItem.objects
        .filter(priority=True)
        .filter(completion_date=None)
        .select_related('patient')
    ).distinct()

    return priority_ai_pts


def user_cases(user, qs):
    '''Build a queryset of the pateints that this user is the case
    manager for
    '''

    qs = models.Patient.objects.filter(
        case_managers=user
    )

    return qs