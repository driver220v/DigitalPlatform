from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Poll(models.Model):
    poll_title = models.CharField(null=False, max_length=128)
    poll_description = models.CharField(null=True, max_length=1024)

    def __str__(self):
        return f"{self.poll_title}"


class PollQuestion(models.Model):
    question_name = models.CharField(max_length=255, null=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return f"{self.question_name}"


class PollQuestionChoices(models.Model):
    choice_name = models.CharField(max_length=255, null=False)
    question = models.ForeignKey(
        PollQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    is_correct = models.BooleanField(default=False, null=False)

    def __str__(self):
        return f"{self.choice_name}"


class PollQuestionAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        PollQuestion, on_delete=models.CASCADE, related_name="answer"
    )
    choice = models.ForeignKey(PollQuestionChoices, on_delete=models.CASCADE)
    # def __str__(self):
    #     return f'{self.user_choice.choice_name}'
