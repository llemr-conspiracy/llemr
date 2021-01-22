from rest_framework import status
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_list_or_404
from django.utils.dateparse import parse_date
from django.db.models.query import EmptyQuerySet

from .serializers import WorkupSerializer

from osler.workup.models import Workup, ClinicDate

class WorkupViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = WorkupSerializer
    queryset = Workup.objects.all().order_by('-id')

    def get_queryset(self):
        queryset = Workup.objects.all().order_by('-id')
        pt = self.request.query_params.get('pt', None)
        if pt is not None:
            queryset = queryset.filter(patient=pt)
        clinic = self.request.query_params.get('clinic', None)
        if clinic is not None:
            objList = get_list_or_404(ClinicDate, clinic_type=clinic)
            new_qs = EmptyQuerySet
            for item in objList:
                new_qs = queryset.filter(clinic_day=item) | new_qs
            queryset = new_qs
            queryset = queryset.order_by('-id')
        date = self.request.query_params.get('date', None)
        if date is not None:
            objList = get_list_or_404(ClinicDate, clinic_date=parse_date(date))
            new_qs = EmptyQuerySet
            for item in objList:
                new_qs = queryset.filter(clinic_day=item) | new_qs
            queryset = new_qs
            queryset = queryset.order_by('-id')
        return queryset

    #search_fields = https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields