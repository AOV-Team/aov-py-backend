# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-03-12 17:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0013_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='photocomment',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='photo.PhotoComment'),
        ),
    ]