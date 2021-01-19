from osler.referral import models

from osler.referral.api import serializers

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

class ReferralViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = serializers.ReferralSerializer
    queryset = models.Referral.objects