from rest_framework import serializers
from osler.workup import models


class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Workup
        fields = ['chief_complaint', 'pk', 'detail_url', 'signer', 'written_datetime']

    detail_url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
