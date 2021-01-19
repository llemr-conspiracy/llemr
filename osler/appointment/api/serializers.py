from rest_framework import serializers
from osler.core.api.common import DynamicFieldsModelSerializer

from osler.appointment import models

class AppointmentSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Appointment
        exclude = []