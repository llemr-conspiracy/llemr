from __future__ import unicode_literals
from builtins import object
from rest_framework import serializers
from pttrack import models
from workup import models as workupModels
from simple_history.models import HistoricalRecords
# from django.urls import reverse


class UrlReverser(object):
    def __init__(self, url_name):
        self.url_name = url_name

    def to_representation(self, obj):
        return reverse(self.url_name, args=(obj.id,))


class lastHistorySerializer(serializers.Serializer):
    history_date = serializers.DateTimeField()


class HistorySerializer(serializers.Serializer):
    last = lastHistorySerializer()


class ClinicDateSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = workupModels.ClinicDate
        exclude = []


class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = workupModels.Workup
        fields = ['chief_complaint', 'clinic_day', 'pk', 'url', 'signer']

    clinic_day = ClinicDateSerializer()
    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)


class CaseManagerSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Provider
        fields = ['name']

    name = serializers.StringRelatedField(read_only=True)


class PatientSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Patient
        exclude = []

    history = HistorySerializer()
    latest_workup = WorkupSerializer()
    gender = serializers.StringRelatedField(read_only=True)
    age = serializers.StringRelatedField(read_only=True)
    name = serializers.StringRelatedField(read_only=True)
    pk = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)
    case_managers = CaseManagerSerializer(many=True)

    # Put urls as model properties because unable to do: patient_url = UrlReverser('patient-detail')
    detail_url = serializers.StringRelatedField(read_only=True)
    update_url = serializers.StringRelatedField(read_only=True)
    activate_url = serializers.StringRelatedField(read_only=True)
