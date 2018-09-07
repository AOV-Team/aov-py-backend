# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-08-28 00:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('utils', '0003_auto_20170210_2357'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('feedback_type', models.CharField(choices=[('A', 'Appreciation'), ('B', 'Bug'), ('F', 'Feature Request')], default='A', max_length=1)),
                ('has_reply', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('reply', models.TextField(blank=True, null=True)),
                ('reply_timestamp', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'verbose_name_plural': 'User Feedback',
            },
        ),
    ]
