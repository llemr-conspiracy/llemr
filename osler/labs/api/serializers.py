from rest_framework import serializers
from osler.core.api.common import DynamicFieldsModelSerializer

from osler.labs import models

class LabSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Lab
        exclude = []