from rest_framework import serializers
from osler.workup import models
from osler.core.api.common import DynamicFieldsModelSerializer


class WorkupSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Workup
        exclude = []

    detail_url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
