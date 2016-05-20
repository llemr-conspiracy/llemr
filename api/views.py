from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
import django.utils.timezone

from pttrack import models as mymodels
from . import serializers
from workup import models as workupmodels
# from rest_framework import status # not needed in the meantime
from rest_framework import generics
import json

import datetime

class PtList(generics.ListAPIView): # read only
    '''
    List patients
    '''

    def get_queryset(self):
        '''
        Restricts returned patients according to query params
        '''
        def bylatestKey(pt):
            latestwu = pt.latest_workup()
            if latestwu == None:
                latestdate = pt.history.last().history_date.date()
            else:
                latestdate = latestwu.clinic_day.clinic_date
            return latestdate

        queryset = mymodels.Patient.objects
        sort = self.request.query_params.get('sort', None)
        list_type = self.request.query_params.get('filter', None) # use var 'list_type' because 'filter' namespace is taken
        # import logging
        # logger = logging.getLogger(__name__)
        # logger.error('sort')
        if sort is not None:
            if str(sort) == 'latest_workup':
                pt_list_latest = list(mymodels.Patient.objects.all())
                pt_list_latest.sort(key = bylatestKey, reverse=True)
                queryset = pt_list_latest
            else:
                queryset = queryset.order_by(sort)

        if list_type is not None:
            list_type = str(list_type)
            if list_type == 'active':
                queryset = queryset.filter(needs_workup__exact=True).order_by('last_name')
            elif list_type == 'ai_active':
                ai_list_active = mymodels.ActionItem.objects.filter(due_date__lte=django.utils.timezone.now().date())
                queryset = list(set([ai.patient for ai in ai_list_active if not ai.done()]))
            elif list_type == 'ai_inactive':
                ai_list_inactive = mymodels.ActionItem.objects.filter(due_date__gt=django.utils.timezone.now().date()).order_by('due_date')
                pt_list_ai_inactive = list(set([ai.patient for ai in ai_list_inactive if not ai.done()]))
                pt_list_ai_inactive.sort(key = lambda pt: pt.inactive_action_items()[-1].due_date)
                queryset = pt_list_ai_inactive
            elif list_type == 'unsigned_workup':
                wu_list_unsigned = workupmodels.Workup.objects.filter(signer__isnull=True).select_related('patient')
                pt_list_unsigned= list(set([wu.patient for wu in wu_list_unsigned]))
                pt_list_unsigned.sort(key = lambda pt: pt.last_name)
                queryset = pt_list_unsigned
        return queryset

    serializer_class = serializers.PatientSerializer
