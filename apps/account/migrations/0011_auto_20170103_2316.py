# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-04 06:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20170103_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gear',
            name='item_make',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='gear',
            name='item_model',
            field=models.CharField(max_length=128),
        ),
    ]
