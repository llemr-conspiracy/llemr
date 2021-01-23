from rest_framework import serializers

from osler.core.api.common import DynamicFieldsModelSerializer
from osler.inventory import models


class UnitSerializer(DynamicFieldsModelSerializer):
  class Meta(object):
    model = models.MeasuringUnit
    exclude = []


class CategorySerializer(DynamicFieldsModelSerializer):
  class Meta(object):
    model = models.DrugCategory
    exclude = []


class ManufacturerSerializer(DynamicFieldsModelSerializer):
  class Meta(object):
    model = models.Manufacturer
    exclude = []
    

class DrugSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Drug
        exclude = []