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

    # unit = UnitSerializer()
    # category = CategorySerializer()
    # manufacturer = ManufacturerSerializer()
    # history = HistorySerializer()

    # dose = serializers.StringRelatedField(read_only=True)  # float
    # stock = serializers.StringRelatedField(read_only=True)  # int
    # expiration_date = serializers.DateField() # date
    # lot_number = serializers.StringRelatedField(read_only=True)


    # add urls??
    # def __init__(self, *args, **kwargs):
    #     super(InventorySerializer, self).__init__(*args, **kwargs)

    #     fields = self.context['request'].query_params.get('fields')
    #     if fields:
    #         fields = fields.split(',')
    #         allowed = set(fields)
    #         existing = set(self.fields.keys())
    #         for field_name in existing - allowed:
    #             self.fields.pop(field_name)
    


    # # Put urls as model properties because unable to do:
    # detail_url = serializers.StringRelatedField(read_only=True)
    # update_url = serializers.StringRelatedField(read_only=True)
    # activate_url = serializers.StringRelatedField(read_only=True)
