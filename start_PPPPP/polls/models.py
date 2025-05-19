import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='created_questions')  # 添加 creator 字段
    allow_multiple_choices = models.BooleanField(default=False)  # 是否允许多选
    min_choices = models.IntegerField(default=1)  # 最少选择几个
    max_choices = models.IntegerField(default=1)  # 最多选择几个
    max_votes_per_user = models.IntegerField(default=1)  # 每个用户最多几张票
    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    max_votes_per_choice = models.IntegerField(default=4)
    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE,default=1)
    allow_multiple_choices = models.BooleanField(default=False)
    class Meta:
        unique_together = ('user', 'choice')