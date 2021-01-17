from rest_framework import serializers
from osler.core.api.common import DynamicFieldsModelSerializer

from osler.demographics import models

class DemographicsSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Demographics
        exclude = []