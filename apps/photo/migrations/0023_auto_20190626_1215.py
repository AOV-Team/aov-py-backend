# Generated by Django 2.0.13 on 2019-06-26 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0022_auto_20190327_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photo_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='photocomment',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='photo.PhotoComment'),
        ),
    ]
