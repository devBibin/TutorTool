# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-13 14:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_conductor_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_system',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='file_conductor_app.FileSystem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='file_system',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='file_conductor_app.FileSystem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='test',
            name='file_system',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='file_conductor_app.FileSystem'),
            preserve_default=False,
        ),
    ]