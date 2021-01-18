# from osler.workup.api import serializers

from osler.inventory.api.serializers import InventorySerializer
from osler.inventory.models import Drug

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet


class InventoryViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = InventorySerializer
    queryset = Drug.objects
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    # @action(detail=False, methods=["GET"])
    # def me(self, request):
    #     serializer = InventorySerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)
