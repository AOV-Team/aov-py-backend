from apps.communication.models import PushMessage
from apps.communication.tasks import send_scheduled_push_notifications
from datetime import timedelta
from django.test import override_settings, TestCase
from django.utils import timezone
from freezegun import freeze_time
from push_notifications.models import APNSDevice
from unittest import mock


@override_settings(CELERY_CACHE_BACKEND='dummy', CELERY_TASK_ALWAYS_EAGER=True)
class TestTaskSendScheduledPushNotifications(TestCase):
    def test_task_send_scheduled_push_notifications_successful(self):
        """
        Test that we can send out a scheduled push notification

        :return: None
        """
        send_at = timezone.now().replace(second=0, microsecond=0) + timedelta(minutes=1)

        device = APNSDevice.objects.create(registration_id='NR3WENEIN2EE33XNTEN34TNSES93NS0E3IS003E3NS8939FS3T')

        message = PushMessage(message='Testing123', send_at=send_at)
        message.save()
        message.device = [device.id]
        message.save()

        # Create more messages that shouldn't send
        PushMessage(message='Testing123', send_at=send_at - timedelta(minutes=1))
        PushMessage(message='Testing123', send_at=send_at + timedelta(minutes=1))

        # Set time to when message should send
        freezer = freeze_time(send_at)
        freezer.start()

        push_message = send_scheduled_push_notifications()

        freezer.stop()

        self.assertEquals(push_message[0].id, message.id)
