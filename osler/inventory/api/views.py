# from osler.workup.api import serializers

from osler.inventory.api.serializers import InventorySerializer
from osler.inventory.models import Drug

from rest_framework import status

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

class InventoryViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = InventorySerializer
    queryset = Drug.objects.all()