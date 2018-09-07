from apps.communication import models as communication_models
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from fcm_django.models import FCMDevice, FCMDeviceQuerySet
from fcm_django.fcm import FCMError
from requests import post


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
    devices = FCMDevice.objects.none()
    if type(recipients) is str:
        if recipients == 'all':
            # To prevent ConnectionErrors,
            # the queryset is passed off to a generator function to return smaller querysets
            all_devices = FCMDevice.objects.all()
            for devices in chunk_devices(all_devices, 100):
                devices = FCMDevice.objects.filter(id__in=devices.values_list("id", flat=True))
                try:
                    devices.send_message(body=message, **kwargs)
                except ConnectionError:
                    continue
                except FCMError:
                    continue

            return
    elif type(recipients) is list or type(recipients) is FCMDeviceQuerySet:
        devices = FCMDevice.objects.filter(id__in=recipients)
    try:
        devices.send_message(body=message, **kwargs)
    except ConnectionError:
        pass
    except FCMError:
        pass


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


def update_device(apns_devices):
    headers = {"authorization": "key={}".format(settings.FCM_DJANGO_SETTINGS["FCM_SERVER_KEY"]),
               "content-type": "application/json"}
    data = {
        "application": "com.artvisual.photoapp",
        "sandbox": False,
        "apns_tokens": list(apns_devices.values_list("registration_id", flat=True))
    }
    response = post("https://iid.googleapis.com/iid/v1:batchImport", headers=headers, json=data)
    if response.status_code == 200:
        for item in response.json()["results"]:
            if item["status"] == "OK":
                return item["registration_token"]

    return False
