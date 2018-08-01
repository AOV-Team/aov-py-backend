from apps.account.models import User
from apps.communication.tasks import send_push_notification
from django.test import override_settings, TestCase
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice
from unittest import mock


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestTaskSendPushNotification(TestCase):
    def setUp(self):
        """
            Method to create necessary test data used across all tests

        :return: None
        """

        user = User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        FCMDevice.objects.create(
            registration_id="1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50",
            type="ios", user=user)
        user1 = User.objects.create_user(email="mytest@artofvisuals.com", password="sup", username="aov2")
        FCMDevice.objects.create(registration_id="1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A",
                                 type="ios", user=user1)

    def tearDown(self):
        """
            Method to clean up data after each test

        :return: None
        """

        User.objects.all().delete()
        FCMDevice.objects.all().delete()

    def test_task_send_push_notification_successful(self):
        """
        Test that we can send a push notification

        :return: None
        """
        # Create test data
        device = FCMDevice.objects.first()

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            message = 'This is a test.'
            recipients = [device.id]

            send_push_notification(message, recipients)


            p.assert_called_with(api_key=None, badge=None, data=None, icon=None,
                                 registration_ids=[device.registration_id], sound=None, title=None,
                                 body=message)

    def test_task_send_push_notification_all(self):
        """
        Test that we can send a push notification to all devices in db

        :return: None
        """
        # Create test data
        FCMDevice.objects.get(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50')
        FCMDevice.objects.get(registration_id='1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A')

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            message = 'This is a test.'

            send_push_notification(message, 'all')

            p.assert_called_with(api_key=None, badge=None, data=None, icon=None,
                                 registration_ids=list(
                                     FCMDevice.objects.all().values_list("registration_id", flat=True)), sound=None,
                                 title=None, body=message)

    def test_task_send_push_notification_specific(self):
        """
        Test that we can send a push notification to specific devices

        :return: None
        """
        # Create test data
        APNSDevice.objects.create(
            registration_id='THISISATESTTHISISATESTTHISISATESTTHISISATESTTHISISATESTAHAAHAAHA')
        devices = FCMDevice.objects.exclude(
            registration_id="1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50")

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            message = 'This is a test.'

            send_push_notification(message, devices)

            p.assert_called_with(body=message, api_key=None, badge=None, data=None, icon=None, title=None,
                                 registration_ids=list(devices.values_list("registration_id", flat=True)), sound=None)
