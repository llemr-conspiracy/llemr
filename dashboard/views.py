# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from workup.models import ClinicDate
from pttrack.models import Patient


def dashboard_dispatch(request):
    """Redirect an incoming user to the appropriate dashboard.

    Falls back to the 'home' url.
    """

    provider_type = request.session['clintype_pk']
    dashboard_dispatch = settings.OSLER_PROVIDERTYPE_DASHBOARDS

    if provider_type in dashboard_dispatch:
        return redirect(dashboard_dispatch[provider_type])
    else:
        return redirect(settings.OSLER_DEFAULT_DASHBOARD)


def dashboard_attending(request):

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

    no_note_patients = Patient.objects.filter(workup=None).order_by('-pk')[:20]

    return render(request,
                  'dashboard/dashboard-attending.html',
                  {'clinics': clinics,
                   'no_note_patients': no_note_patients
                   })
