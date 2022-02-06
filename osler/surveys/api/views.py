from osler.surveys.models import Survey, Question, Choice
from osler.surveys.api.serializers import SurveySerializer, QuestionSerializer, ChoiceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

class ChoiceViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    List all choices
    """
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

class QuestionViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    List all questions, or create a new question
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class SurveyViewSet(viewsets.ModelViewSet):
    """
    List the survey, it's description and all questions associated
    """
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    
