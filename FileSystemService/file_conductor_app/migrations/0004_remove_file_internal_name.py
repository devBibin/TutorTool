# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-26 15:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('file_conductor_app', '0003_auto_20180526_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='internal_name',
        ),
    ]