from rest_framework import serializers
from . import models
from workup import models as workupModels
from simple_history.models import HistoricalRecords

class lastHistorySerializer(serializers.Serializer): #FIXME how to serialize date
	history_date = serializers.DateTimeField()

class HistorySerializer(serializers.Serializer):
	last = lastHistorySerializer()

class ClinicDateSerializer(serializers.ModelSerializer):
	class Meta:
		model = workupModels.ClinicDate

class WorkupSerializer(serializers.ModelSerializer):
	class Meta:
		model = workupModels.Workup
		fields = ['chief_complaint', 'clinic_day', 'pk']

	clinic_day = ClinicDateSerializer()

class PatientSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Patient

	history = HistorySerializer() # <------ vs this
	latest_workup = WorkupSerializer()
	gender = serializers.StringRelatedField(read_only=True)
	age = serializers.StringRelatedField(read_only=True)
	name = serializers.StringRelatedField(read_only=True)
	pk = serializers.StringRelatedField(read_only=True)
	status = serializers.StringRelatedField(read_only=True)
	