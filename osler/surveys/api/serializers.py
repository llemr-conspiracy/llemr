from rest_framework import serializers
from osler.surveys.models import Survey, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(read_only=False, many=True)

    class Meta:
        model = Question
        fields = ['id', 'survey', 'question', 'choices', 'question_type']


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(read_only=True, many=True)

    class Meta:
        model = Survey
        fields = ['title', 'description', 'questions']
