from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeProfileViewSetGET(TestCase):
    """
    Test GET /api/me/profile
    """
    def test_me_profile_view_set_get_successful(self):
        """
        Test that we can get user's profile

        :return: None
        """
        # Create user and data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/profile')
        result = request.data['result']

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)
        self.assertIn('gear', result)

    def test_me_profile_view_set_get_does_not_exist(self):
        """
        Test that we get 404 if user does not have a profile

        :return: None
        """
        # Create user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/profile')

        self.assertEquals(request.status_code, 404)


class TestMeProfileViewSetPATCH(TestCase):
    """
    Test PATCH /api/me/profile
    """
    def test_me_profile_view_set_patch_successful(self):
        """
        Test that we can update user's profile

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'bio': 'Foo'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.patch('/api/me/profile', data=payload, format='json')
        result = request.data['result']

        # Test return data
        self.assertEquals(result['bio'], 'Foo')
        self.assertEquals(result['cover_image'], None)
        self.assertEquals(result['gear'], None)

        # Check db entry too
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertEquals(updated_profile.bio, 'Foo')

    def test_me_profile_view_set_patch_not_found(self):
        """
        Test that we get 404 if profile does not exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'bio': 'Foo'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.patch('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 404)

    def test_me_profile_view_set_patch_sanitize(self):
        """
        Test that we cannot change user

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        profile1 = account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        user2 = account_models.User.objects.create_user(email='mr@mypapaya.io', password='pass', username='aov_hovy')
        profile2 = account_models.Profile.objects.create_or_update(user=user2, bio='Haha')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'id': profile2.id,
            'bio': 'Foo'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.patch('/api/me/profile', data=payload, format='json')
        result = request.data['result']

        self.assertEquals(result['bio'], 'Foo')

        # Check db entry
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertEquals(updated_profile.id, profile1.id)
