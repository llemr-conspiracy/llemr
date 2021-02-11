from rest_framework import serializers
from osler.surveys.models import Survey, Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id','survey', 'question']

    # def to_representation(self, value):
    #     return value.question

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(read_only=True, many=True)

    class Meta:
        model = Survey
        fields = ['title', 'description', 'questions']