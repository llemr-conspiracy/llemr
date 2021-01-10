from rest_framework import serializers
from osler.core import models
from osler.workup.api.serializers import WorkupSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

class LastHistorySerializer(serializers.Serializer):
    history_date = serializers.DateTimeField()


class HistorySerializer(serializers.Serializer):
    last = LastHistorySerializer()


class CaseManagerSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = get_user_model()
        fields = ['name']

    name = serializers.StringRelatedField(read_only=True)


class PatientSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Patient
        exclude = ['case_managers']

    # history = HistorySerializer()
    latest_workup = WorkupSerializer()
    # gender = serializers.StringRelatedField(read_only=True)
    age = serializers.StringRelatedField(read_only=True)
    name = serializers.StringRelatedField(read_only=True)
    pk = serializers.StringRelatedField(read_only=True)
    status = serializers.StringRelatedField(read_only=True)
    #case_managers = CaseManagerSerializer(many=True)

    # Put urls as model properties because unable to do:
    detail_url = serializers.StringRelatedField(read_only=True)
    update_url = serializers.StringRelatedField(read_only=True)
    activate_url = serializers.StringRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(PatientSerializer, self).__init__(*args, **kwargs)

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
        languages =  validated_data.pop('languages')
        ethnicities = validated_data.pop('ethnicities')
        patient = models.Patient.objects.create(**validated_data)
        for language in languages:
            lang = get_object_or_404(models.Language, name=language)
            patient.languages.add(lang)
        for ethnicity in ethnicities:
            eth = get_object_or_404(models.Ethnicity, name=ethnicity)
            patient.ethnicities.add(eth)
        return patient
    
    def update(self, instance, validated_data):
        languages =  validated_data.pop('languages')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.languages.clear()
       
        for language in languages:
            lang = get_object_or_404(models.Language, name=language)
            instance.languages.add(lang)
        instance.save()
        return instance

    def get_extra_kwargs(self):
        extra_kwargs = super(PatientSerializer, self).get_extra_kwargs()
        action = self.context['view'].action

        #this makes certain fields read-only for update and partial_update
        read_only_fields = ['first_name','middle_name','last_name','date_of_birth', 'ethnicities']
        if action in ['update', 'partial_update']:
            for field_name in read_only_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs