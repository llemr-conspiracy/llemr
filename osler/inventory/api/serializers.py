from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from osler.core.api.common import DynamicFieldsModelSerializer
from osler.core.api.serializers import HistorySerializer
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
    

class InventorySerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Drug
        exclude = []