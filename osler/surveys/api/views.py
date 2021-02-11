from osler.surveys.models import Survey, Question
from osler.surveys.api.serializers import SurveySerializer, QuestionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

class QuestionViewSet(viewsets.ModelViewSet):
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

    
