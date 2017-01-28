from django.db import models
from push_notifications.models import APNSDevice


class PushMessage(models.Model):
    """
    Push message to be sent out at a specific time
    """
    device = models\
        .ManyToManyField(APNSDevice, blank=True,
                         help_text='iOS devices to send message to. Message will be sent to all devices if empty',
                         verbose_name='devices')
    message = models.TextField()
    send_at = models.DateTimeField()
