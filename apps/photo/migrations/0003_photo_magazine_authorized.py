# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-01 03:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0002_auto_20170224_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='magazine_authorized',
            field=models.BooleanField(default=True),
        ),
    ]
