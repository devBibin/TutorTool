# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group

class TeacherInfo(models.Model):
	user = models.ForeignKey(User)
	additional_info = models.CharField(max_length=300)

class StudentInfo(models.Model):
	user = models.ForeignKey(User)
	additional_info = models.CharField(max_length=300)

class StudentToTeacher(models.Model):
	student = models.ForeignKey(User, related_name='student')
	teacher = models.ForeignKey(User, related_name='teacher')
	status = models.CharField(max_length=20, default="Pending")
