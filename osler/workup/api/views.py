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

    # def create(self, request):
    #     #These fields all needed to be popped because they require foreign keys or many to many relationships.
    #     #These could be added to exclude in the future depending on API needs.
    #     print(request.data)
    #     serializer = WorkupSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #     return Response(serializer.data)
        # other_volunteer = validated_data.pop('other_volunteer')
        # diagonsis_categories = validated_data.pop('diagnosis_categories')
        # referral_type = validated_data.pop('referral_type')
        # referral_location = validated_data.pop('referral_location')

        #Must find or create ClinicDate object
        # clinic_day = validated_data.pop('clinic_day')
        # clinic_instance, created = ClinicDate.objects.get_or_create(clinic_date=clinic_day['clinic_date'],clinic_type=clinic_day['clinic_type'])
        # workup = Workup.objects.create(**validated_data, clinic_day=clinic_instance)
        # return workup
    # lookup_field = "username"

    # @action(detail=False, methods=["GET"])
    # def me(self, request):
    #     serializer = UserSerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)