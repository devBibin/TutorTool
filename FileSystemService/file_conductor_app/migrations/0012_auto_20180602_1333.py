# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-02 13:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_conductor_app', '0011_auto_20180602_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='filesystem',
            name='status',
            field=models.CharField(default='surfing', max_length=30),
        ),
        migrations.AddField(
            model_name='filesystem',
            name='temp_transfer_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='filesystem',
            name='temp_transfer_type',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
    ]
