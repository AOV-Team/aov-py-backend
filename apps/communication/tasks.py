from apps.communication import models as communication_models
from celery import shared_task
from django.db.models import QuerySet
from django.utils import timezone
from push_notifications.apns import APNSError, APNSServerError
from push_notifications.models import APNSDevice, APNSDeviceQuerySet


def chunk_devices(queryset, size: int):
    """
        Yields a QuerySet of count 'size'

    :param queryset: QuerySet of objects
    :param size: Size of sub-QuerySet to be returned
    :return: QuerySet of count 'size'
    """
    for i in range(0, queryset.count(), size):
        yield queryset[i:i + size]


@shared_task(name='send_push_notification')
def send_push_notification(message, recipients, **kwargs):
    """
    Send a notification

    :param message: message to send
    :param recipients: str ('all') or list of APNS device ids
    :param kwargs: keyword arguments to pass into send_message()
    :return: None
    """
    devices = APNSDevice.objects.none()
    if type(recipients) is str:
        if recipients == 'all':
            # To prevent ConnectionErrors,
            # the queryset is passed off to a generator function to return smaller querysets
            all_devices = APNSDevice.objects.all()
            for devices in chunk_devices(all_devices, 100):
                devices = APNSDevice.objects.filter(id__in=devices.values_list("id", flat=True))
                try:
                    devices.send_message(message, **kwargs)
                except ConnectionError as e:
                    print("ERROR: ", e)
                    continue
                except (APNSError, APNSServerError) as e:
                    print("ERROR: ", e)
                    continue

            return
    elif type(recipients) is list or type(recipients) is APNSDeviceQuerySet:
        devices = APNSDevice.objects.filter(id__in=recipients)
    devices.send_message(message, **kwargs)


@shared_task(name='send_scheduled_push_notifications')
def send_scheduled_push_notifications():
    """
    Check for push notifications to be sent out.

    :return: None
    """
    now = timezone.now().replace(second=0, microsecond=0)

    # Query for messages to be sent out now
    messages = communication_models.PushMessage.objects.filter(send_at=now)

    for message in messages:
        send_push_notification.delay(message.message, list(message.device.all().values_list('id', flat=True)))

    return messages
