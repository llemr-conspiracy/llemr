from rest_framework import serializers
from osler.core import models
from osler.workup.api.serializers import WorkupSerializer


class LastHistorySerializer(serializers.Serializer):
    history_date = serializers.DateTimeField()


class HistorySerializer(serializers.Serializer):
    last = LastHistorySerializer()


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

    # Put urls as model properties because unable to do:
    detail_url = serializers.StringRelatedField(read_only=True)
    update_url = serializers.StringRelatedField(read_only=True)
    activate_url = serializers.StringRelatedField(read_only=True)
