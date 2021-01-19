from rest_framework import serializers
from osler.core.api.common import DynamicFieldsModelSerializer

from osler.referral import models

class ReferralSerializer(DynamicFieldsModelSerializer):
    class Meta(object):
        model = models.Referral
        exclude = []