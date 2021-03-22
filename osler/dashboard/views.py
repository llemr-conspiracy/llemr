# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from osler.workup.models import Workup
from osler.core.models import Patient
from osler.core.views import all_patients

from osler.users.utils import get_active_role


def dashboard_dispatch(request):
    """Redirect an incoming user to the appropriate dashboard.

    Falls back to the 'home' url.
    """

    active_role = get_active_role(request)
    dashboard_dispatch = settings.OSLER_ROLE_DASHBOARDS

    if active_role.name in dashboard_dispatch:
        return redirect(dashboard_dispatch[active_role.name])
    else:
        return redirect(settings.OSLER_DEFAULT_DASHBOARD)


def dashboard_active(request):
    """Calls active patient dashboard filtered by patients needing workups."""
    
    return all_patients(request, title='Active Patients', active=True)


def dashboard_attending(request):
    
    wu_list = Workup.objects.filter(attending=request.user)
    paginator = Paginator(wu_list, settings.OSLER_WORKUPS_PER_PAGE,
                          allow_empty_first_page=True)

    page = request.GET.get('page')
    try:
        wu_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        wu_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        wu_page = paginator.page(paginator.num_pages)


    no_note_patients = Patient.objects.filter(workup=None, encounter__status__is_active=True).order_by('-pk')

    return render(request,
                  'dashboard/dashboard-attending.html',
                  {'wu_page': wu_page,
                   'no_note_patients': no_note_patients
                   })
