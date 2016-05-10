from rest_framework import serializers
from . import models
from workup import models as workupModels
from simple_history.models import HistoricalRecords

# class HistorySerializer(serializers.Serializer):
# 	history = serializers.HistoricalRecords()

class ClinicDateSerializer(serializers.ModelSerializer):
	class Meta:
		model = workupModels.ClinicDate

class WorkupSerializer(serializers.ModelSerializer):
	clinic_day = ClinicDateSerializer()
	class Meta: # this defines the fields that get serialized/deserialized
		model = workupModels.Workup
		fields = ['chief_complaint', 'clinic_day']

class PatientSerializer(serializers.ModelSerializer):
	# history = HistorySerializer() # <------ vs this
	latest_workup = WorkupSerializer()
	# latest_history = serializers.
	# latest_workup = serializers.latest_workup # <------ test this
	# history = serializers.HistoricalRecords()
	class Meta: # this defines the fields that get serialized/deserialized
		model = models.Patient
		# fields = ['history','latest_workup'] # <------ vs this
		# exclude = ['needs_workup'] # maybe not here, might need for update

	# ModelSerializer gives simple default implementations of create() and update()
	# # We actually don't need these? Since it's just for the all-patients view?
	# def create(self, validated_data):
	# 	"""
 #        Create and return a new `Patient` instance, given the validated data.
 #        """
 #        return Patient.objects.create(**validated_data) # not sure if I should do this, cos only the tests seem to do this

	# def update(self, instance, validated_data):
	# 	"""
 #        Update and return an existing `Patient` instance, given the validated data.
 #        """
 #        # FIXME update every field
 #        instance.save()
 #        return instance
