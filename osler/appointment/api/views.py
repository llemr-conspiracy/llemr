from osler.appointment import models

from osler.appointment.api import serializers

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

class AppointmentViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = serializers.AppointmentSerializer
    queryset = models.Appointment.objects