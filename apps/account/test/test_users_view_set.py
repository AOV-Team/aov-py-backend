from apps.account import models as account_models
from django.test import TestCase
from rest_framework.test import APIClient


class TestUsersViewSetPOST(TestCase):
    """
    Test /api/users POST (user creation)
    """
    def test_users_view_set_post_basic_successful(self):
        """
        Successful /api/users POST.
        Log user in to make sure password is correctly set

        :return: None
        """
        # Create gear
        gear = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')

        client = APIClient()

        payload = {
            'email': 'mr@mypapaya.io',
            'gear': [gear.id],
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')
        result = request.data

        self.assertEquals(request.status_code, 201)
        self.assertIn('email', result)
        self.assertEquals(len(result['gear']), 1)
        self.assertIn('username', result)

        user = account_models.User.objects.get(email='mr@mypapaya.io')

        self.assertEquals(len(user.gear.all()), 1)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

        # Attempt to log user in
        login_request = client.post('/api/auth',
                                    data={'email': 'mr@mypapaya.io', 'password': 'WhoWantsToBeAMillionaire?'},
                                    format='json')
        login_result = login_request.data

        self.assertIn('token', login_result)

    def test_users_view_set_post_cannot_set_superuser(self):
        """
        Test that super user cannot be created via API

        :return: None
        """
        client = APIClient()

        payload = {
            'email': 'mrsneakytest@mypapaya.io',
            'is_superuser': False,
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        user = account_models.User.objects.get(email='mrsneakytest@mypapaya.io')

        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_users_view_set_post_full_successful(self):
        """
        Successful /api/users POST with full data

        :return: None
        """
        client = APIClient()

        with open('apps/common/test/data/photos/cover.jpg', 'rb') as image:
            payload = {
                'age': 23,
                'avatar': image,
                'email': 'mrtest@mypapaya.io',
                'first_name': 'Martin',
                'last_name': 'Ronquillo',
                'location': 'Boise',
                'password': 'WhoWantsToBeAMillionaire?',
                'social_name': 'aov',
                'social_url': 'http://instagram.com/aov',
                'username': 'aov_hov',
                'website_url': 'https://artofvisuals.com'
            }

            request = client.post('/api/users', data=payload, format='multipart')

        result = request.data

        self.assertEquals(request.status_code, 201)
        self.assertIn('avatar', result)
        self.assertIn('email', result)
        self.assertIn('social_name', result)
        self.assertIn('social_url', result)
        self.assertIn('username', result)
        self.assertIn('website_url', result)

        user = account_models.User.objects.get(email='mrtest@mypapaya.io')

        self.assertEquals(user.age, 23)
        self.assertIsNotNone(user.avatar)
        self.assertEquals(user.email, 'mrtest@mypapaya.io')
        self.assertEquals(user.first_name, 'Martin')
        self.assertTrue(user.is_active)
        self.assertEquals(user.last_name, 'Ronquillo')
        self.assertEquals(user.location, 'Boise')
        self.assertEquals(user.social_name, 'aov')
        self.assertEquals(user.social_url, 'http://instagram.com/aov')
        self.assertEquals(user.username, 'aov_hov')
        self.assertEquals(user.website_url, 'https://artofvisuals.com')
        self.assertFalse(user.is_superuser)

    def test_users_view_set_post_app_data_successful(self):
        """
        Successful /api/users POST with the data that we expect from the app

        :return: None
        """
        client = APIClient()

        payload = {
            'age': 20,
            'email': 'nortongumbo@u.boisestate.edu',
            'is_active': 1,
            'location': 'Boise',
            'password': 'pass',
            'social_name': '@ngumbo3',
            'username': 'gumbno'
        }

        request = client.post('/api/users', data=payload)
        result = request.data

        self.assertEquals(request.status_code, 201)
        self.assertIn('email', result)
        self.assertIn('social_name', result)
        self.assertIn('username', result)

        user = account_models.User.objects.get(email='nortongumbo@u.boisestate.edu')

        self.assertEquals(user.age, 20)
        self.assertTrue(user.is_active)
        self.assertEquals(user.location, 'Boise')
        self.assertEquals(user.social_name, '@ngumbo3')
        self.assertEquals(user.username, 'gumbno')
        self.assertFalse(user.is_superuser)

    def test_users_view_set_post_already_exists(self):
        """
        /api/users POST (user already exists)

        :return: None
        """
        # Create user
        account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Attempt to create user via API
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hovy'
        }

        request = client.post('/api/users', data=payload, format='json')
        result = request.data

        self.assertEquals(request.status_code, 409)
        self.assertIn('Email already exists', result['message'])

    def test_users_view_set_post_email_and_username_already_exist(self):
        """
        /api/users POST (user email + username already exist)

        :return: None
        """
        # Create user
        account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Attempt to create user via API
        client = APIClient()

        payload = {
            'email': 'mrtest@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')
        result = request.data

        self.assertEquals(request.status_code, 409)

        self.assertIn('Email already exists', result['message'])
        self.assertIn('Username already exists', result['message'])

    def test_users_view_set_post_bad_request(self):
        """
        /api/users POST (bad request)

        :return: None
        """
        # Attempt to create user via API with invalid payload
        client = APIClient()

        request = client.post('/api/users', data={'email': 'bad@test.com'}, format='json')
        self.assertEquals(request.status_code, 400)

    def test_users_view_set_post_case_insensitive(self):
        """
        Test that user emails are case insensitive

        :return: None
        """
        client = APIClient()

        payload = {
            'email': 'mr@mypapaya.io',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        payload = {
            'email': 'Mr@mypapaya.io',
            'password': 'Millionaire',
            'username': 'aov'
        }

        request = client.post('/api/users', data=payload, format='json')

        self.assertEquals(request.status_code, 409)

    def test_users_view_set_post_case_insensitive_2(self):
        """
        Test that user emails are case insensitive

        :return: None
        """
        client = APIClient()

        payload = {
            'email': 'Spencer.a.marsh@gmail.com',
            'password': 'WhoWantsToBeAMillionaire?',
            'username': 'aov_hov'
        }

        request = client.post('/api/users', data=payload, format='json')

        self.assertEquals(request.status_code, 201)

        payload = {
            'email': 'spencer.a.marsh@gmail.com',
            'password': 'Millionaire',
            'username': 'aov'
        }

        request = client.post('/api/users', data=payload, format='json')

        self.assertEquals(request.status_code, 409)
