from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.question_text

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'choice')