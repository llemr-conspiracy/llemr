from rest_framework import serializers
from osler.workup import models


class ClinicDateSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.ClinicDate
        exclude = []


class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Workup
        fields = ['chief_complaint', 'clinic_day', 'pk', 'url', 'signer']

    clinic_day = ClinicDateSerializer()
    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
