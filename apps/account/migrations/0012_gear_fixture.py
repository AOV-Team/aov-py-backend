# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'gear', app_label='account')


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0011_auto_20170103_2316'),
    ]

    operations = [
        migrations.RunPython(load_fixture)
    ]
