from rest_framework import serializers
from osler.surveys.models import Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['survey', 'question']

