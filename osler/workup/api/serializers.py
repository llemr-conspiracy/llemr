from rest_framework import serializers
from osler.workup import models


class ClinicDateSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.ClinicDate
        exclude = []


class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Workup
        # fields = ['chief_complaint', 'clinic_day', 'pk', 'url', 'signer']
        exclude = []

    clinic_day = ClinicDateSerializer()
    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)

    def create(self, validated_data):
        #These fields all needed to be popped because they require foreign keys or many to many relationships.
        #So will have to implement another way to utilize them.
        #These could be added to exclude in the future depending on API needs.
        other_volunteer = validated_data.pop('other_volunteer')
        diagonsis_categories = validated_data.pop('diagnosis_categories')
        referral_type = validated_data.pop('referral_type')
        referral_location = validated_data.pop('referral_location')

        #Must find or create ClinicDate object
        clinic_day = validated_data.pop('clinic_day')
        clinic_instance, created = models.ClinicDate.objects.get_or_create(clinic_date=clinic_day['clinic_date'],clinic_type=clinic_day['clinic_type'])
        workup = models.Workup.objects.create(**validated_data, clinic_day=clinic_instance)
        return workup

    def update(self, instance, validated_data):
        # other_volunteer = validated_data.pop('other_volunteer')
        # diagonsis_categories = validated_data.pop('diagnosis_categories')
        # referral_type = validated_data.pop('referral_type')
        # referral_location = validated_data.pop('referral_location')
        # clinic_day = validated_data.pop('clinic_day')
        # clinic_instance, created = models.ClinicDate.objects.get_or_create(clinic_date=clinic_day['clinic_date'],clinic_type=clinic_day['clinic_type'])
        if serializer.is_valid():
            serializer.save()
        return serializer
