from apps.account.models import User
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from fcm_django.models import FCMDevice
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

        FCMDevice.objects.create(registration_id='ARESTNAIERSNTEARNSTEIARNSTINSREATNAERISNTEARIST')
        FCMDevice.objects.create(registration_id='TNAIERSNTEATINSREATNAERISNEARSNTEI3EIN3EINENEEN')

        client = APIClient()
        client.force_login(user)

        request = client.get('/api/devices')
        results = request.data['results']

        self.assertIn('count', request.data)
        self.assertIn('next', request.data)

        self.assertEquals(len(results), 2)

    def test_devices_view_set_get_non_admin(self):
        """
        Test that non-admin cannot access this endpoint

        :return: None
        """
        # Test data
        user = User.objects.create_user('aov@aov.com', 'pass')
        FCMDevice.objects.create(registration_id='ARESTNAIERSNTEARNSTEIARNSTINSREATNAERISNTEARIST')
        FCMDevice.objects.create(registration_id='TNAIERSNTEATINSREATNAERISNEARSNTEI3EIN3EINENEEN')

        token = test_helpers.get_token_for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/devices')

        self.assertEquals(request.status_code, 403)

    def test_devices_view_set_get_query(self):
        """
        Test that we can get devices by user email, name, or username/social name

        :return: None
        """
        # Test data
        superuser = User.objects.create_superuser('aov@aov.com', 'pass')

        user = User.objects.create_user('mrtest@aov.com', '@yesman', 'pass')
        user.social_name = '@ahyeah'
        user.save()

        user2 = User.objects.create_user('random@aov.com', '@random', 'pass')
        user2.first_name = 'Bob'
        user2.last_name = 'Person'
        user2.save()

        d1 = FCMDevice.objects.create(user=user, registration_id='ARESTNAIERSNTEARNSTEIARNSTINSREATNAERISNTEARIST')
        d2 = FCMDevice.objects.create(user=user2, registration_id='TNAIERSNTEATINSREATNAERISNEARSNTEI3EIN3EINENEEN')

        client = APIClient()
        client.force_login(superuser)

        # First query, username
        request = client.get('/api/devices?q=yesman')
        results = request.data['results']

        self.assertIn('count', request.data)
        self.assertIn('next', request.data)

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['id'], d1.id)

        # Second query, email
        request = client.get('/api/devices?q=random@aov.com')
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['id'], d2.id)

        # Third query, social name
        request = client.get('/api/devices?q=yeah')
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['id'], d1.id)

        # Fourth query, first name
        request = client.get('/api/devices?q=bob')
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['id'], d2.id)

        # Fifth query, last name
        request = client.get('/api/devices?q=person')
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['id'], d2.id)


class TestDevicesViewSetPOST(TestCase):
    def test_devices_view_set_post_successful(self):
        """
        Test that we can save a device token for a user

        :return: None
        """
        # Create test data
        registration_id = '1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50'
        user = User.objects.create_user('aov@aov.com', 'pass')

        token = test_helpers.get_token_for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/devices', data={'registration_id': registration_id})

        self.assertEquals(request.status_code, 201)

        # query db
        tokens = FCMDevice.objects.all()

        self.assertEquals(tokens.count(), 1)

        token = tokens.first()

        self.assertEquals(token.user, user)
        self.assertEquals(token.registration_id, registration_id)

    def test_devices_view_set_post_missing_registration_id(self):
        """
        Test that we get HTTP 400 if registration_id is missing

        :return: None
        """
        # Create test data
        user = User.objects.create_user('aov@aov.com', 'pass')

        token = test_helpers.get_token_for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/devices', data={})

        self.assertEquals(request.status_code, 400)

        # query db
        tokens = FCMDevice.objects.all()

        self.assertEquals(tokens.count(), 0)
