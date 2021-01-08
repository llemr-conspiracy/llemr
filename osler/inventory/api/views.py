# from osler.workup.api import serializers

from osler.inventory.api.serializers import InventorySerializer
from osler.inventory.models import Drug

from rest_framework import status, viewsets
from rest_framework.decorators import action

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    queryset = Drug.objects.all()

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    # @action(detail=False, methods=["GET"])
    # def me(self, request):
    #     serializer = InventorySerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)
