from rest_framework import serializers
from . import models
from workup import models as workupModels
from simple_history.models import HistoricalRecords

class lastHistorySerializer(serializers.Serializer): #FIXME how to serialize date
	history_date = serializers.DateTimeField()
	# history_date = serializers.CharField(max_length=200)

class HistorySerializer(serializers.Serializer):
	last = lastHistorySerializer()
	# class Meta:
	# 	model = HistoricalRecords()
	# 	fields = ['last']

class ClinicDateSerializer(serializers.ModelSerializer):
	class Meta:
		model = workupModels.ClinicDate

class WorkupSerializer(serializers.ModelSerializer):
	clinic_day = ClinicDateSerializer()
	class Meta:
		model = workupModels.Workup
		fields = ['chief_complaint', 'clinic_day', 'pk']

class PatientSerializer(serializers.ModelSerializer):
	history = HistorySerializer() # <------ vs this
	latest_workup = WorkupSerializer()
	# latest_history = serializers.
	# latest_workup = serializers.latest_workup # <------ test this
	# history = serializers.HistoricalRecords()
	class Meta:
		model = models.Patient
		fields = ['history','age','latest_workup', 'name', 'last_name', 'pk', 'gender', 'status', 'needs_workup'] # <------ vs this
