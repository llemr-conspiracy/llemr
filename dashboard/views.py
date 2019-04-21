# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from workup.models import ClinicDate
from pttrack.models import Patient

# class AttendingDashboard(ListView):

#     model = ClinicDate
#     template_name = 'dashboard/attending-dashboard.html'

#     def get_queryset(self):

#         provider = self.request.user.provider

#         qs = super(AttendingDashboard, self)\
#             .get_queryset()\
#             .filter(workup__attending=provider)\
#             .prefetch_related('workup_set', 'clinic_type')

#         return qs


def attending_dashboard(request):

    provider = request.user.provider

    clinic_list = ClinicDate.objects.filter(workup__attending=provider)

    paginator = Paginator(clinic_list, settings.OSLER_CLINIC_DAYS_PER_PAGE,
                          allow_empty_first_page=True)

    page = request.GET.get('page')
    try:
        clinics = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        clinics = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        clinics = paginator.page(paginator.num_pages)

    no_note_patients = Patient.objects.filter(workup=None).order_by('pk')

    # id2creation_date = {
    #     l['id']: l['history_date']
    #     for l in Patient.history
    #         .filter(id__in=no_note_patients)
    #         .values('id', 'history_date')
    #         .order_by('-history_date')
    # }

    return render(request,
                  'dashboard/attending-dashboard.html',
                  {'clinics': clinics,
                   'no_note_patients': no_note_patients
                   })

# class AttendingDashboard(ListView):

#     model = Patient
#     template_name = 'dashboard/attending-dashboard.html'

#     def get_queryset(self):

#         provider = self.request.user.provider

#         qs = super(AttendingDashboard, self) \
#             .get_queryset() \
#             .filter(workup__signer=None) \
#             .filter(workup__attending=provider)

#         return qs
