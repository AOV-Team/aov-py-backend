# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-10-15 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0009_auto_20180914_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='directmessage',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
