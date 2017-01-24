from celery import task
from push_notifications.models import APNSDevice


@task(name='send_push_notification')
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
            devices = APNSDevice.objects.all()
    elif type(recipients) is list:
        devices = APNSDevice.objects.filter(id__in=recipients)

    devices.send_message(message, **kwargs)
