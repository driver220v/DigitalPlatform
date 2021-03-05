from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Poll(models.Model):
    name = models.CharField(null=False, max_length=128)
    poll_description = models.CharField(null=True, max_length=1024)

    def __str__(self):
        return f'{self.name}'


class PollQuestion(models.Model):
    question_name = models.CharField(max_length=255, null=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll')

    def __str__(self):
        return f'{self.question_name}'


class PollQuestionChoices(models.Model):
    choice_name = models.CharField(max_length=255, null=False)
    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE, related_name='choices')


class QuestionAnswer(models.Model):
    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    choice_status = models.BooleanField(null=False, default=False)