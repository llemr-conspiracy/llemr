from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class Question(models.Model):

    class QuestionType(models.TextChoices):
        TEXT = 'FREE_RESPONSE'
        MC = 'MULTIPLE_CHOICE'
        DATE = 'DATE_RESPONSE'

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.TEXT)
    required = models.BooleanField()

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.SET_NULL, null=True, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO: link patient/encounter information


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=1000)  # if mc/checkboxes, this is the string given in the post request
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.question:
            return f"{self.text} - {self.question.question}"
        return f"{self.text} - <question deleted>"
