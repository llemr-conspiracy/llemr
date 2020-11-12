from rest_framework import serializers
from osler.workup import models
from osler.core.models import ReferralType, ReferralLocation

class ReferralLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralLocation

class ClinicDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClinicDate
        exclude = []

class WorkupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workup
        exclude = []

    clinic_day = ClinicDateSerializer()
    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)

    
    def __init__(self, *args, **kwargs):
        super(WorkupSerializer, self).__init__(*args, **kwargs)

        #to request just specific fields
        #ex: /api/workups/id/?fields=clinic_day,chief_complaint  for an individual workup
        # or /api/workups/?fields=clinic_day,chief_complaint  for list view 
        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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
        
        referral_location_instance = ReferralLocation.objects.filter(name=referral_location)
        
        workup = models.Workup.objects.create(**validated_data, clinic_day=clinic_instance)
        # workup.referral_location.add(referral_location_instance)
        return workup

    def update(self, instance, validated_data):
        other_volunteer = validated_data.pop('other_volunteer')
        diagonsis_categories = validated_data.pop('diagnosis_categories')
        referral_type = validated_data.pop('referral_type')
        referral_location = validated_data.pop('referral_location')
        clinic_day = validated_data.pop('clinic_day')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_extra_kwargs(self):
        extra_kwargs = super(WorkupSerializer, self).get_extra_kwargs()
        action = self.context['view'].action

        #this makes certain fields read-only for update and partial_update
        #how to do clinic_day since it is a nested object
        read_only_fields = ['patient','written_datetime','author','author_type']
        if action in ['update', 'partial_update']:
            for field_name in read_only_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs