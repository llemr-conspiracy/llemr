from osler.demographics import models

from osler.demographics.api import serializers

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

class DemographicsViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = serializers.DemographicsSerializer
    queryset = models.Demographics.objects