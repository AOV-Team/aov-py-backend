# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'mail-categories', app_label='utils')
    call_command('loaddata', 'mail-templates', app_label='utils')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.RunPython(load_fixture)
    ]
