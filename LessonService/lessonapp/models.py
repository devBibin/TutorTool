from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group

class Lesson(models.Model):
	teacher = models.IntegerField()
	student = models.IntegerField()
	info = models.CharField(max_length = 100)


class Homework(models.Model):
	lesson = models.ForeignKey(Lesson)
	object_type = models.CharField(max_length=30)
	object_id = models.IntegerField()

