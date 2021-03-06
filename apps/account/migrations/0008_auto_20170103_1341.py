# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-03 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_starreduser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(blank=True, null=True)),
                ('make', models.TextField(max_length=128)),
                ('model', models.TextField(max_length=128)),
                ('public', models.BooleanField(default=True)),
                ('reviewed', models.BooleanField(default=False)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'ordering': ('make', 'model'),
                'verbose_name_plural': 'gear',
            },
        ),
        migrations.RemoveField(
            model_name='profile',
            name='gear',
        ),
    ]
