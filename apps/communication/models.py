from apps.account.models import User
from apps.common.models import EditMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fcm_django.models import FCMDevice
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
        ("T", "Tagged"),
        ("U", "Upvote")
    )

    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    message = models.TextField()
    receiver = models.ForeignKey(APNSDevice, blank=True, null=True)
    fcm_receiver = models.ForeignKey(FCMDevice, blank=True, null=True)
    sender = models.ForeignKey(User, blank=True, null=True)

    viewed = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "ID: {} ACTION: {}".format(self.id, self.action)

    class Meta:
        verbose_name_plural = "Notification Records"

