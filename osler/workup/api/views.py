from rest_framework import status
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from .serializers import WorkupSerializer

from osler.workup.models import Workup, ClinicDate

class WorkupViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin,GenericViewSet):
    serializer_class = WorkupSerializer
    queryset = Workup.objects.all()
