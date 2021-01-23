#TO DO OTHER VOLUNTEER, LIST ORDERING
#IGNORE REFERRAL STUFF FOR NOW

#FIELDS THAT ARE NOT WORKING PROPERLY
#signer - not sure what this should be
#other volunteer - not sure how to make foreign key to user model what to search for
#author and author_type seem to be working but might need validation

from rest_framework import serializers
from osler.workup import models
from osler.core.api.common import DynamicFieldsModelSerializer
from osler.core.models import ReferralType, ReferralLocation
from django.shortcuts import get_object_or_404

class ReferralLocationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ReferralLocation
    
class WorkupSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Workup
        exclude = []

    detail_url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
    other_volunteer = serializers.StringRelatedField(read_only=True, many=True)
    diagnosis_categories = serializers.StringRelatedField(read_only=True, many=True)

    # def create(self, validated_data):
    #     #These fields all needed to be popped because they require foreign keys or many to many relationships.
    #     other_volunteer = validated_data.pop('other_volunteer')
    #     diagnosis_categories = validated_data.pop('diagnosis_categories')
    #     referral_location = validated_data.pop('referral_location')
    #     referral_type = validated_data.pop('referral_type')

    #     #Must find or create ClinicDate object
    #     clinic_day = validated_data.pop('clinic_day')
    #     clinic_instance, created = models.ClinicDate.objects.get_or_create(clinic_date=clinic_day['clinic_date'],clinic_type=clinic_day['clinic_type'])
        
    #     #create workup
    #     workup = models.Workup.objects.create(**validated_data, clinic_day=clinic_instance)
        
    #     #add diagnosis categories
    #     for diagnosis_category in diagnosis_categories:
    #         diag = get_object_or_404(models.DiagnosisType, name=diagnosis_category)
    #         workup.diagnosis_categories.add(diag)

    #     #potentially should be changed to get_or_create depending on if we want to accept new referral locations in this way
    #     for location in referral_location:
    #         loc = get_object_or_404(models.ReferralLocation, name=location)
    #         workup.referral_location.add(loc)
    #     for t in referral_type:
    #         type_object = get_object_or_404(models.ReferralType, name=t)
    #         workup.referral_type.add(type_object)

    #     return workup

    # def update(self, instance, validated_data):
    #     diagnosis_categories = validated_data.pop('diagnosis_categories')
    #     clinic_day = validated_data.pop('clinic_day')
    #     #clinic_day isn't actually updated so it's safe not to have it as read-only but not great
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.diagnosis_categories.clear()
    #     for diagnosis_category in diagnosis_categories:
    #         diag = get_object_or_404(models.DiagnosisType, name=diagnosis_category)
    #         instance.diagnosis_categories.add(diag)
    #     instance.save()
    #     return instance

    # def get_extra_kwargs(self):
    #     extra_kwargs = super(WorkupSerializer, self).get_extra_kwargs()
    #     action = self.context['view'].action

    #     #this makes certain fields read-only for update and partial_update
    #     read_only_fields = ['patient','written_datetime','author','author_type','other_volunteer','referral_type','referral_location','attending']
    #     if action in ['update', 'partial_update']:
    #         for field_name in read_only_fields:
    #             kwargs = extra_kwargs.get(field_name, {})
    #             kwargs['read_only'] = True
    #             extra_kwargs[field_name] = kwargs
    #     return extra_kwargs