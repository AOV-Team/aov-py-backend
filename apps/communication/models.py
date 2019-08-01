from apps.account.models import User
from apps.common.models import EditMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice


class Conversation(EditMixin):
    """
        Model to connect multiple messages and users to a single thread
    """
    participants = models.ManyToManyField(User, related_name="participants")
    message_count = models.PositiveIntegerField()


class DirectMessage(EditMixin):
    """
        Model for a user-to-user direct message object

    """
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="recipient", on_delete=models.CASCADE)
    message = models.TextField()
    conversation = models.ForeignKey(Conversation, related_name="conversation", on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    index = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Direct Messages"


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
        ("D", "Direct Message"),
        ("F", "Follower"),
        ("R", "Feedback Reply"),
        ("T", "Tagged"),
        ("U", "Upvote")
    )

    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    message = models.TextField()
    receiver = models.ForeignKey(APNSDevice, blank=True, null=True, on_delete=models.SET_NULL)
    fcm_receiver = models.ForeignKey(FCMDevice, blank=True, null=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    viewed = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "ID: {} ACTION: {}".format(self.id, self.action)

    class Meta:
        verbose_name_plural = "Notification Records"

