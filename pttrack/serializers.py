from rest_framework import serializers
from . import models
from simple_history.models import HistoricalRecords

class PatientSerializer(serializers.ModelSerializer):

	# latest_history = serializers.
	# latest_workup = 
	# history = serializers.HistoricalRecords()
	class Meta: # this defines the fields that get serialized/deserialized
		model = models.Patient
		# fields = ['latest_workup']
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
