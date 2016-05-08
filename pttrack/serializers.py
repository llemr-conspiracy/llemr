from rest_framework import serializers
from . import models

class PatientSerializer(serializers.ModelSerializer):
	class Meta: # this defines the fields that get serialized/deserialized
		model = models.Patient
		exclude = ['needs_workup'] # maybe not here, might need for update

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
