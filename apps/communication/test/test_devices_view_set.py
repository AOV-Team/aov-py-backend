from apps.account.models import User
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from push_notifications.models import APNSDevice
from rest_framework.test import APIClient


class TestDevicesViewSetGET(TestCase):
    def test_devices_view_set_get_successful(self):
        """
        Test that we can get devices

        :return: None
        """
        # Test data
        user = User.objects.create_superuser('aov@aov.com', 'pass')

        APNSDevice.objects.create(registration_id='ARESTNAIERSNTEARNSTEIARNSTINSREATNAERISNTEARIST')
        APNSDevice.objects.create(registration_id='TNAIERSNTEATINSREATNAERISNEARSNTEI3EIN3EINENEEN')

        client = APIClient()
        client.force_login(user)

        request = client.get('/api/devices')
        results = request.data['results']

        self.assertIn('count', request.data)
        self.assertIn('count', request.data)

        self.assertEquals(len(results), 2)

    def test_devices_view_set_get_non_admin(self):
        """
        Test that non-admin cannot access this endpoint

        :return: None
        """
        # Test data
        user = User.objects.create_user('aov@aov.com', 'pass')
        APNSDevice.objects.create(registration_id='ARESTNAIERSNTEARNSTEIARNSTINSREATNAERISNTEARIST')
        APNSDevice.objects.create(registration_id='TNAIERSNTEATINSREATNAERISNEARSNTEI3EIN3EINENEEN')

        token = test_helpers.get_token_for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/devices')

        self.assertEquals(request.status_code, 403)
