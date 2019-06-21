from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import PushNotificationRecord
from django.test import TestCase, override_settings
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice
from rest_framework.test import APIClient
from unittest import mock


class TestUserFollowersViewSetGET(TestCase):
    def test_user_followers_view_set_get_successful(self):
        """
        Test that we can retrieve all followers for a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')
        user_2 = account_models.User.objects.create_user(email='prince@aov.com', social_name='@wbp', username='wbp')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower = [user_1, user_2]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/followers'.format(target_user.id), format='json')
        results = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertIn('count', request.data)
        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)

        for result in results:
            if result['username'] != user_1.username and result['username'] != user_2.username:
                self.fail('Unidentified follower')

    def test_user_followers_view_set_get_does_not_exist(self):
        """
        Test that we get 404 if user does not exist

        :return: None
        """
        # Test data
        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/followers'.format(99999), format='json')

        self.assertEquals(request.status_code, 404)

    def test_user_followers_view_set_get_self(self):
        """
        Test that a user can see their own followers

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')
        user_2 = account_models.User.objects.create_user(email='prince@aov.com', social_name='@wbp', username='wbp')

        # Follow target user
        target_user.follower = [user_1, user_2]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(target_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/followers'.format(target_user.id), format='json')
        results = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertIn('count', request.data)
        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)

        for result in results:
            if result['username'] != user_1.username and result['username'] != user_2.username:
                self.fail('Unidentified follower')

    def test_user_followers_view_set_get_unauthenticated(self):
        """
        Test that an unauthenticated user can retrieve followers

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')
        user_2 = account_models.User.objects.create_user(email='prince@aov.com', social_name='@wbp', username='wbp')

        # Follow target user
        target_user.follower = [user_1, user_2]
        target_user.save()

        # Get data from endpoint
        client = APIClient()

        request = client.get('/api/users/{}/followers'.format(target_user.id), format='json')
        results = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertIn('count', request.data)
        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)

        for result in results:
            if result['username'] != user_1.username and result['username'] != user_2.username:
                self.fail('Unidentified follower')

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestUserFollowersViewSetPOST(TestCase):
    def tearDown(self):
        APNSDevice.objects.all().delete()

    def test_user_followers_view_set_post_successful(self):
        """
        Test that we can follow a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')
        device = FCMDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=target_user,
            type="ios")

        # Follow target user
        target_user.follower = [user_1]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Wrap the call in a mock so we aren't sending real push notifications during tests
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:

            # Get data from endpoint
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

            self.assertEquals(request.status_code, 201)

            # Assert the mocked call for push notification occurred.
            p.assert_called_with(api_key=None, badge=None, data=None, icon=None,
                                 registration_ids=[device.registration_id], sound=None, title=None,
                                 body='mr started following you, aov_hov.')

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(len(followers), 2)
        self.assertEqual(PushNotificationRecord.objects.count(), 1)

        for follower in followers:
            if follower.id != access_user.id and follower.id != user_1.id:
                self.fail('Unidentified follower')

    def test_user_followers_view_set_post_no_apns_device(self):
        """
            Unit test to make sure the endpoint still functions correctly even if the push notification code fails

        :return: No return value
        """

        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower = [user_1]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            # Get data from endpoint
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

            self.assertEquals(request.status_code, 201)
            p.assert_not_called()

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(len(followers), 2)
        self.assertEqual(PushNotificationRecord.objects.count(), 0)

        for follower in followers:
            if follower.id != access_user.id and follower.id != user_1.id:
                self.fail('Unidentified follower')

    def test_user_followers_view_set_post_already_following(self):
        """
        Test that we get a 409 status code if we are already following a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower = [access_user]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 409)

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(followers.count(), 1)

        follower = followers.first()

        self.assertEquals(follower.id, access_user.id)

    def test_user_followers_view_set_post_does_not_exist(self):
        """
        Test that we get 404 if user does not exist

        :return: None
        """
        # Test data
        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/followers'.format(999999), format='json')

        self.assertEquals(request.status_code, 404)

    def test_user_followers_view_set_post_unauthenticated(self):
        """
        Test that only an authenticated user can follow a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')

        # Get data from endpoint
        client = APIClient()

        request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 401)

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(followers.count(), 0)

    def test_user_followers_view_set_follow_back_post_successful(self):
        """
        Test that I can follow one of my followers

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower = [access_user]
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(target_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/followers'.format(access_user.id), format='json')

        self.assertEquals(request.status_code, 201)
