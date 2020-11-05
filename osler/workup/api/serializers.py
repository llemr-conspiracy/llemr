from rest_framework import serializers
from osler.workup import models


class ClinicDateSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.ClinicDate
        exclude = []



#to make certain fields write_once, aka only specified on post and read-only on put
#https://stackoverflow.com/questions/16522845/write-once-read-only-field
#http://blog.qax.io/write-once-fields-with-django-rest-framework/

#either need to use get extra kwargs or write a separate serializer :(
#i think id rather use kwargs just cuz then have to figure out type of request and then supply specific serializer

class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Workup
        #fields = ['chief_complaint', 'clinic_day', 'pk', 'url', 'signer', 'patient', 'author_id']
        exclude = []

    clinic_day = ClinicDateSerializer()
    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)

    #to request just specific fields
    #ex: /api/workups/id/?fields=clinic_day,chief_complaint  for an individual workup
    # or /api/workups/?fields=clinic_day,chief_complaint  for list view 
    def __init__(self, *args, **kwargs):
        super(WorkupSerializer, self).__init__(*args, **kwargs)

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
        workup = models.Workup.objects.create(**validated_data, clinic_day=clinic_instance)
        return workup

    def update(self, instance, validated_data):
        read_only_fields = ['patient',]
        # other_volunteer = validated_data.pop('other_volunteer')
        # diagonsis_categories = validated_data.pop('diagnosis_categories')
        # referral_type = validated_data.pop('referral_type')
        # referral_location = validated_data.pop('referral_location')
        # clinic_day = validated_data.pop('clinic_day')
        # clinic_instance, created = models.ClinicDate.objects.get_or_create(clinic_date=clinic_day['clinic_date'],clinic_type=clinic_day['clinic_type'])
        other_volunteer = validated_data.pop('other_volunteer')
        diagonsis_categories = validated_data.pop('diagnosis_categories')
        referral_type = validated_data.pop('referral_type')
        referral_location = validated_data.pop('referral_location')
        clinic_day = validated_data.pop('clinic_day')
        instance.pmh = validated_data['pmh']
        instance.psh = validated_data['psh']
        instance.save()
        return instance

    #need to do, probably similar to form validation
    # def validate(self, data):
    #     return data

    def get_extra_kwargs(self):
        extra_kwargs = super(WorkupSerializer, self).get_extra_kwargs()
        action = self.context['view'].action

        #how to do clinic_day since it is a nested object
        read_only_fields = ['patient','written_datetime','author','author_type']
        if action in ['update', 'partial_update']:
            for field_name in read_only_fields:
                kwargs = extra_kwargs.get(field_name, {})
                kwargs['read_only'] = True
                extra_kwargs[field_name] = kwargs

        return extra_kwargs