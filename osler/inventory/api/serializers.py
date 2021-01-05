from rest_framework import serializers
from osler.inventory import models

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

class InventorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Drug
        exclude = []

    name = 
    unit = 
    dose = 
    stock = 
    expiration_date = 
    lot_number =
    category = 
    manufacturer = 
    history = 

    # add urls??


    # history = HistorySerializer()
    # gender = serializers.StringRelatedField(read_only=True)
    # age = serializers.StringRelatedField(read_only=True)
    # name = serializers.StringRelatedField(read_only=True)
    # pk = serializers.StringRelatedField(read_only=True)
    # actionitem_status = serializers.StringRelatedField(read_only=True)
    # case_managers = CaseManagerSerializer(many=True)

    # # Put urls as model properties because unable to do:
    # detail_url = serializers.StringRelatedField(read_only=True)
    # update_url = serializers.StringRelatedField(read_only=True)
    # activate_url = serializers.StringRelatedField(read_only=True)