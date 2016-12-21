# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-17 01:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0003_photo_original_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]