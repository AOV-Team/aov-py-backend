from apps.communication.tasks import send_push_notification
from django.test import override_settings, TestCase
from push_notifications.models import APNSDevice
from unittest import mock
import uuid


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestTaskSendPushNotification(TestCase):
    def test_task_send_push_notification_successful(self):
        """
        Test that we can send a push notification

        :return: None
        """
        # Create test data
        device = APNSDevice.objects\
            .create(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50')

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            message = 'This is a test.'
            recipients = [device.id]

            send_push_notification(message, recipients)

            p.assert_called_with(alert=message,
                                 registration_ids=['1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50'])

    def test_task_send_push_notification_all(self):
        """
        Test that we can send a push notification to all devices in db

        :return: None
        """
        # Create test data
        used_ids = list()
        for num in range(1, 10**6):
            reg_id = ''.join(x.strip() for x in str(uuid.uuid4()).split('-'))
            used_ids.append(reg_id)
            APNSDevice.objects.create(registration_id=reg_id)
            # APNSDevice.objects.create(registration_id='1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A')

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            message = 'This is a test.'

            send_push_notification(message, 'all')

            # p.assert_called_with(alert=message,
            #                      registration_ids=[
            #                          '1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50',
            #                          '1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A'])
            p.assert_called_with(alert=message,
                                 registration_ids=used_ids)

    def test_task_send_push_notification_specific(self):
        """
        Test that we can send a push notification to specific devices

        :return: None
        """
        # Create test data
        APNSDevice.objects.create(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50')
        d1 = APNSDevice.objects\
            .create(registration_id='1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A')
        d2 = APNSDevice.objects\
            .create(registration_id='THISISATESTTHISISATESTTHISISATESTTHISISATESTTHISISATESTAHAAHAAHA')

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            message = 'This is a test.'

            send_push_notification(message, [d1.id, d2.id])

            p.assert_called_with(alert=message,
                                 registration_ids=[
                                     '1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A',
                                     'THISISATESTTHISISATESTTHISISATESTTHISISATESTTHISISATESTAHAAHAAHA'])
