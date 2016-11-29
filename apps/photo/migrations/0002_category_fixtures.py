# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'categories', app_label='photo')
    call_command('loaddata', 'photo_feeds', app_label='photo')


class Migration(migrations.Migration):
    dependencies = [
        ('photo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture)
    ]
