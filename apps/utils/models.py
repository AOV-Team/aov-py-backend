from apps.account import models as account_models
from apps.common.models import EditMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserAction(models.Model):
    ACTION_CHOICES = (
        ('photo_click', 'Photo Click'),
        ('photo_flag', 'Photo Flag'),
        ('photo_imp', 'Photo Impression'),
    )

    user = models.ForeignKey(account_models.User)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Feedback(EditMixin):
    FEEDBACK_CHOICES = (
        ("A", "Appreciation"),
        ("B", "Bug"),
        ("F", "Feature Request"),
    )

    feedback_type = models.CharField(choices=FEEDBACK_CHOICES, max_length=1, default="A")
    has_reply = models.BooleanField(default=False)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    reply_timestamp = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(account_models.User)

    class Meta:
        verbose_name_plural = "User Feedback"
        default_permissions = ('add', 'change', 'delete', 'view')