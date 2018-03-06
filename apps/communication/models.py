from apps.common.models import EditMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from push_notifications.models import APNSDevice


class PushMessage(models.Model):
    """
    Push message to be sent out at a specific time
    """
    device = models.ManyToManyField(
        APNSDevice, blank=True,
        help_text='iOS devices to send message to. Message will be sent to all devices if empty',
        verbose_name='devices')
    message = models.TextField()
    send_at = models.DateTimeField()


class PushNotificationRecord(EditMixin):
    """
    History of push messages sent to a user
    """
    ACTION_CHOICES = (
        ("A", "AoV Pick"),
        ("C", "Comment"),
        ("F", "Follower"),
        ("U", "Upvote")
    )

    receiver = models.ForeignKey(APNSDevice)
    message = models.TextField()
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

