from apps.account import models as account_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserAction(models.Model):
    ACTION_CHOICES = (
        ('photo_click', 'Photo Click'),
        ('photo_imp', 'Photo Impression'),
    )

    user = models.ForeignKey(account_models.User)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
