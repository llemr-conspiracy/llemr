from osler.inventory.api.serializers import DrugSerializer
from osler.inventory.models import Drug

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet


class DrugViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = DrugSerializer
    queryset = Drug.objects
