from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from django.contrib.sessions.models import Session
from rest_framework.test import APIClient
import datetime


class TestMeProfileViewSetGET(test_helpers.SessionTestCase):
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
        # token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'pass'
        }

        request = client.post('/api/auth', data=payload, format='json')
        login = request.data
        client.credentials(HTTP_AUTHORIZATION='Token ' + login["token"])

        # Create the session
        s = client.session
        s.update({
            "expire_date": '2018-05-29',
            "session_key": s.session_key,
            "last_activity": (datetime.datetime.now() - datetime.timedelta(minutes=95)).timestamp()
        })
        s.save()

        request = client.get('/api/me/profile')
        result = request.data

        self.assertIn('bio', result)
        self.assertIn('cover_image', result)
        self.assertNotIn('gear', result)

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
    def setUp(self):
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

    def tearDown(self):
        account_models.User.objects.all().delete()
        account_models.Profile.objects.all().delete()

    def test_me_profile_view_set_patch_successful(self):
        """
        Test that we can update user's profile

        :return: None
        """
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        with open('apps/common/test/data/photos/cover.jpg', 'rb') as image:
            payload = {
                'bio': 'Foo',
                'cover_image': image,
            }

            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.patch('/api/me/profile', data=payload, format='multipart')

        result = request.data

        # Test return data
        self.assertEquals(result['bio'], 'Foo')

        # Check db entry too
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertEquals(updated_profile.bio, 'Foo')

    def test_me_profile_view_set_patch_image(self):
        """
        Test that we can update user image

        :return: None
        """
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        with open('apps/common/test/data/photos/cover.jpg', 'rb') as image:
            payload = {
                'cover_image': image,
            }

            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.patch('/api/me/profile', data=payload, format='multipart')

        result = request.data

        self.assertIn('cover_image', result)

        # Check db entry too
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertIsNotNone(updated_profile.cover_image)

    def test_me_profile_view_set_patch_bad_request(self):
        """
        Test that we get 400 if invalid

        :return: None
        """
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'cover_image': 'Foo'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.patch('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

    def test_me_profile_view_set_patch_gear(self):
        """
        Test that we get HTTP 400 if attempting to edit gear using this endpoint

        :return: None
        """
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'bio': 'Foo',
            'gear': {
                'name': 'Nifty Fifty'
            }
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.patch('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

    def test_me_profile_view_set_patch_not_found(self):
        """
        Test that we get 404 if profile does not exist

        :return: None
        """
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")

        # Delete the profile
        account_models.Profile.objects.all().delete()

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
        # Retrieve the user
        user = account_models.User.objects.get(username="aov_hov")
        profile1 = account_models.Profile.objects.get(user=user, bio='I am a tester.')

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
        result = request.data

        self.assertEquals(result['bio'], 'Foo')

        # Check db entry
        updated_profile = account_models.Profile.objects.get(user=user)

        self.assertEquals(updated_profile.id, profile1.id)


class TestMeProfileViewSetPOST(TestCase):
    """
    Test POST /api/me/profile
    """
    def test_me_profile_view_set_post_successful(self):
        """
        Test that we can create user's profile

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'bio': 'This is cool!',
                'cover_image': image
            }

            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/me/profile', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['user'], user.id)
        self.assertEquals(result['bio'], 'This is cool!')
        self.assertIsNotNone(result['cover_image'])

        # Query for entry
        profile = account_models.Profile.objects.filter(user=user)

        self.assertEquals(len(profile), 1)
        self.assertEquals(profile[0].user, user)

    def test_me_profile_view_set_post_already_created(self):
        """
        Test that we cannot create more than one profile for a user

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.Profile.objects.create_or_update(user=user, bio='I am a tester.')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'bio': 'This is cool!'
        }

        request = client.post('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 409)

    def test_me_profile_view_set_post_bad_request_invalid_field(self):
        """
        Test that we can still save even if there's an invalid field in payload

        :return: None
        """
        # Create test user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'about': 'Awesome',
                'bio': 'This is cool!',
                'cover_image': image
            }

            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/me/profile', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['bio'], 'This is cool!')
        self.assertIsNotNone(result['cover_image'])

        # Query for entry
        profile = account_models.Profile.objects.filter(user=user)

        self.assertEquals(len(profile), 1)
        self.assertEquals(profile[0].user, user)

    def test_me_profile_view_set_post_bad_request_no_valid_fields(self):
        """
        Test that we get 400 if no valid fields

        :return: None
        """
        # Create test user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'about': 'Fail'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

    def test_me_profile_view_set_post_gear_not_allowed(self):
        """
        Test that we get HTTP 400 if user submits gear (need to use /api/me/gear/)

        :return: None
        """
        # Create test user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'bio': 'This is cool!',
            'gear': '["Nikon", "50mm Lens"]'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/profile', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

    def test_me_profile_view_set_post_no_image(self):
        """
        Test that we save without an image

        :return: None
        """
        # Create test user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()

        payload = {
            'bio': 'This is cool!'
        }

        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/profile', data=payload, format='json')
        result = request.data

        self.assertEquals(result['bio'], 'This is cool!')

        # Query for entry
        profile = account_models.Profile.objects.filter(user=user)

        self.assertEquals(len(profile), 1)
        self.assertEquals(profile[0].user, user)
