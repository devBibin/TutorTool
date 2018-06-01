# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class FileSystem(models.Model):
    master = models.ForeignKey(User)
    creation_date = models.DateTimeField(default = timezone.now)
    max_size = models.IntegerField(default = 500)
    cur_size = models.IntegerField(default = 0)


class Directory(models.Model):
	file_system = models.ForeignKey(FileSystem)
	parent = models.ForeignKey("self", null=True, default=None)
	name = models.CharField(max_length = 30, default="Unknown")
	creation_date = models.DateTimeField(default = timezone.now)
	last_upd = models.DateTimeField(default = timezone.now)
	upd_type = models.CharField(max_length=30, default="")

	is_deleted = models.BooleanField(default = False)
	is_editable = models.BooleanField(default = True)
	can_be_deleted = models.BooleanField(default = True)


class File(models.Model):
	file_system = models.ForeignKey(FileSystem)
	parent = models.ForeignKey(Directory, null=True, default=None)
	
	name = models.CharField(max_length = 100)
	path = models.CharField(max_length= 200)
	creation_date = models.DateTimeField(default = timezone.now)
	last_upd = models.DateTimeField(default = timezone.now)
	upd_type = models.CharField(max_length=30, default="")

	is_deleted = models.BooleanField(default = False)
	is_editable = models.BooleanField(default = True)
	can_be_deleted = models.BooleanField(default = True)


class Test(models.Model):
	file_system = models.ForeignKey(FileSystem, )
	parent = models.ForeignKey(Directory, null=True, default=None)
	name = models.CharField(max_length = 30, default="Unknown")
	creation_date = models.DateTimeField(default = timezone.now)
	last_upd = models.DateTimeField(default = timezone.now)
	upd_type = models.CharField(max_length=30, default="")

	is_deleted = models.BooleanField(default = False)


class Question(models.Model):
	file_system = models.ForeignKey(FileSystem)
	parent = models.ForeignKey(Directory, null=True, default=None)
	name = models.CharField(max_length = 30, default="Unknown")
	creation_date = models.DateTimeField(default = timezone.now)
	last_upd = models.DateTimeField(default = timezone.now)
	upd_type = models.CharField(max_length=30, default="")

	bodytext = models.CharField(max_length = 150)
	answer_type = models.CharField(max_length=10)
	rate = models.IntegerField()

	is_deleted = models.BooleanField(default = False)


class QuestionFiles(models.Model):
	file = models.ForeignKey(File)
	question = models.ForeignKey(Question)


class QuestionChoices(models.Model):
	question = models.ForeignKey(Question)
	text = models.CharField(max_length=150)
	is_true = models.BooleanField()


class QuestionToTest(models.Model):
	question = models.ForeignKey(Question)
	test = models.ForeignKey(Test)
	q_index_in_test = models.IntegerField()