from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class Question(models.Model):

    class QuestionType(models.TextChoices):
        TEXT = 'Short Answer'  # includes  all other special input fields (num,date,time...)
        CHECKBOXES = 'Select Many'
        RADIOS = 'Multiple Choice'
        TEXTAREA = 'Paragraph'

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.TEXT)
    required = models.BooleanField(default=False)
    allow_other = models.BooleanField(default=False)  # will put 'other' option for checkboxes/radios
    input_type = models.CharField(default='text', max_length=20)  # for text: <input type={{ input_type }} ..>

    def add_choice(self, choiceText):
        self.choice_set.create(text=choiceText)

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, null=True, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    author_role = models.ForeignKey(Group, on_delete=models.PROTECT)
    # patient = models.ForeignKey(Patient, on_delete=models.PROTECT)

    class Meta:
        get_latest_by = "created_at"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=1000)  # if mc/checkboxes, this is the string given in the post request
    question = models.ForeignKey(Question, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.text} - {self.question.question}"
