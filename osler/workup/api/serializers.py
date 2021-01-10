from rest_framework import serializers
from osler.workup import models


class WorkupSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Workup
        fields = ['chief_complaint', 'pk', 'url', 'signer', 'written_datetime']

    url = serializers.StringRelatedField(read_only=True)
    signer = serializers.StringRelatedField(read_only=True)
