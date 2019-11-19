from functools import partial

import django.utils.timezone
from django.db.models.functions import Least
from django.db.models import Q, Min, Count

from rest_framework import generics

from pttrack import models as coremodels
from workup import models as workupmodels
from referral import models as referrals

from . import serializers


def active_patients_filter(qs):
    '''Filter a queryset of patients for those that are listed as
    active. This is used to display a subset of patients for voluneers
    giving care on a particular clinic day (to hide the giant list of
    pts).
    '''

    print('hi')
    return qs.filter(needs_workup__exact=True).order_by('last_name')


def active_ai_patients_filter(qs):
    '''Filter a queryset of patients for those that have overdue action
    items.
    '''

    ai_qs = coremodels.ActionItem.objects \
        .filter(due_date__lte=django.utils.timezone.now().date()) \
        .filter(completion_date=None) \
        .select_related('patient')

    referral_qs = referrals.FollowupRequest.objects \
        .filter(due_date__lte=django.utils.timezone.now().date()) \
        .filter(completion_date=None) \
        .select_related('patient')

    pts_with_active_ais = coremodels.Patient.objects \
        .filter(actionitem__in=ai_qs) \
        .distinct().annotate(soonest_due_date=Min('actionitem__due_date'))

    for pt in list(pts_with_active_ais):
        print(pt.last_name)
        print(pt.soonest_due_date)

    pts_with_active_referrals = coremodels.Patient.objects \
        .filter(followuprequest__in=referral_qs) \
        .distinct().annotate(soonest_due_date=Min('followuprequest__due_date'))

    patient_dict = {p: p.soonest_due_date for p in pts_with_active_ais}

    for p in pts_with_active_referrals:
        if p not in patient_dict:
            patient_dict[p] = p.soonest_due_date
        else:
            patient_dict[p] = min(patient_dict[p], p.soonest_due_date)

    out_list = [t[0] for t in sorted(
        [(p, soonest_due_date) for p, soonest_due_date
         in patient_dict.iteritems()],
        key=lambda x: x[1])
    ]

    return out_list


def inactive_ai_patients_filter(qs):
    '''Build a queryset of patients for those that have active action
    items due in the future.
    '''

    future_ai_pts = coremodels.Patient.objects.filter(
        actionitem__in=coremodels.ActionItem.objects
            .filter(due_date__gt=django.utils.timezone.now().date())
            .filter(completion_date=None)
            .select_related('patient')
        ).annotate(soonest_due_date=Min('actionitem__due_date'))

    future_referral_pts = coremodels.Patient.objects.filter(
        followuprequest__in=referrals.FollowupRequest.objects
            .filter(due_date__gt=django.utils.timezone.now().date())
            .filter(completion_date=None)
            .select_related('patient')
        ).annotate(soonest_due_date=Min('followuprequest__due_date'))

    print([p.soonest_due_date for p in future_ai_pts])
    print([p.soonest_due_date for p in future_referral_pts])
    patient_dict = {p: p.soonest_due_date for p in future_ai_pts}

    for p in future_referral_pts:
        if p not in patient_dict:
            patient_dict[p] = p.soonest_due_date
        else:
            patient_dict[p] = min(patient_dict[p], p.soonest_due_date)

    print(patient_dict)

    out_list = [t[0] for t in sorted(
        [(p, soonest_due_date) for p, soonest_due_date
         in patient_dict.iteritems()],
        key=lambda x: x[1])
    ]

    return out_list


def unsigned_workup_patients_filter(qs):
    '''Build a queryset that returs a list of patients with an unsigned
    workup.
    '''

    wu_qs = workupmodels.Workup.objects \
        .filter(signer__isnull=True) \
        .order_by('last_name') \
        .select_related('patient')  # optimization only

    return coremodels.Patient.objects.filter(workup__in=wu_qs)

def priority_ai_patients_filter(qs):
    '''Build a queryset that returs a list of patients with a high priority
    action item.
    '''

    priority_ai_pts = coremodels.Patient.objects.filter(
        actionitem__in=coremodels.ActionItem.objects
        .filter(priority=True)
        .filter(completion_date=None)
        .select_related('patient')
        ).distinct()

    return priority_ai_pts


def user_cases(user, qs):
    '''Build a queryset of the pateints that this user is the case
    manager for
    '''

    qs = coremodels.Patient.objects.filter(
        case_managers=user.provider
        )

    return qs


class PtList(generics.ListAPIView):  # read only
    '''
    List patients
    '''

    serializer_class = serializers.PatientSerializer

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

        def bylatestKey(pt): # This doesn't sort by latest time, just latest date
            latestwu = pt.latest_workup()
            if latestwu is None:
                latestdate = pt.history.last().history_date.date()
            else:
                latestdate = latestwu.clinic_day.clinic_date
            return latestdate

        queryset = coremodels.Patient.objects
        sort = self.request.query_params.get('sort', None)
        filter_name = self.request.query_params.get('filter', None)

        if sort is not None:
            if str(sort) == 'latest_workup':
                pt_list_latest = list(coremodels.Patient.objects.all())
                pt_list_latest.sort(key=bylatestKey, reverse=True)
                queryset = pt_list_latest
            else:
                queryset = queryset.order_by(sort)

        queryset = filter_funcs[filter_name](queryset)

        return queryset
