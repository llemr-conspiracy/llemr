from rest_framework import serializers
from osler.workup import models
from osler.core.api.common import DynamicFieldsModelSerializer

class BasicWorkupSerializer(DynamicFieldsModelSerializer):
    
    class Meta:
        model = models.Workup
        exclude = []

    author = serializers.StringRelatedField(read_only=True)
    author_type = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
    detail_url = serializers.StringRelatedField(read_only=True)
