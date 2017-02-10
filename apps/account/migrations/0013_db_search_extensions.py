from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0012_gear_fixture'),
    ]

    operations = [
      TrigramExtension(),
      UnaccentExtension(),
    ]
