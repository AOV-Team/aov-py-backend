from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeViewSetGET(TestCase):
    """
    Test /api/me
    """
    def test_me_view_set_get_successful(self):
        """
        Successful /api/me GET

        :return:
        """
        # Create data
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')

        user = account_models.User.objects.create_user(email='test@test.com', social_name='aeon', username='aov_hov')
        user.gear = [gear_1, gear_2]

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me')
        result = request.data

        self.assertEquals(result['email'], user.email)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['social_name'], user.social_name)
        self.assertEquals(result['username'], user.username)


class TestMeViewSetPATCH(TestCase):
    """
    Test PATCH /api/me
    """
    def test_me_view_set_patch_successful(self):
        """
        Test that we can update user's data

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Gear
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'email': user.email,
            'age': 22,
            'gear': [gear_1.id, gear_2.id],
            'username': user.username
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data

        self.assertEquals(result['age'], 22)
        self.assertEquals(len(result['gear']), 2)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.age, 22)
        self.assertEquals(len(updated_user.gear.all()), 2)

    def test_me_view_set_patch_avatar(self):
        """
        Test that we can update user's photo

        :return: None
        """
        # Create data
        user = account_models.User.objects\
            .create_user(avatar=Photo(open('apps/common/test/data/photos/cover.jpg', 'rb')), age=23,
                         email='test@test.com', social_name='aeon', username='aov_hov')

        self.assertIsNotNone(user.avatar)
        avatar = user.avatar

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/avatar.jpg', 'rb') as image:
            payload = {
                'avatar': image,
                'email': user.email,
                'username': user.username
            }

            request = client.patch('/api/me', data=payload, format='multipart')

        result = request.data
        print('RR', result)

        self.assertIsNotNone(result['avatar'])

        # Should have compressed and saved image
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertIsNotNone(updated_user.avatar)
        self.assertNotEqual(avatar, updated_user.avatar)

    def test_me_view_set_patch_gear(self):
        """
        Test that we can update user's gear

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')
        user.save()
        user.gear = [account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II'),
                     account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')]
        user.save()

        # Gear
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS Rebel T6')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='A7')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'gear': [gear_1.id, gear_2.id]
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data

        self.assertEquals(result['age'], 23)
        self.assertEquals(len(result['gear']), 2)

        # Gear
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 4)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.age, 23)
        self.assertEquals(len(updated_user.gear.all()), 2)
        self.assertEquals(updated_user.gear.all()[0].id, gear_1.id)

    def test_me_view_set_patch_password(self):
        """
        Test that we can update user's password

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')
        user.set_password('ohyeah')
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'existing_password': 'ohyeah',
            'password': 'haha'
        }

        request = client.patch('/api/me', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Attempt to log in with new password
        login_request = client.post('/api/auth', data={'email': user.email, 'password': 'haha'}, format='json')

        self.assertEquals(login_request.status_code, 201)

    def test_me_view_set_patch_password_no_existing_pass(self):
        """
        Test that we cannot update password if existing password is not provided

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')
        user.set_password('ohyeah')
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'password': 'haha'
        }

        request = client.patch('/api/me', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Attempt to log in with old password (not changed)
        login_request = client.post('/api/auth', data={'email': user.email, 'password': 'ohyeah'}, format='json')

        self.assertEquals(login_request.status_code, 201)

    def test_me_view_set_patch_password_incorrect_pass(self):
        """
        Test that we cannot update password if existing password is not correct

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')
        user.set_password('ohyeah')
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'existing_password': 'srts',
            'password': 'haha'
        }

        request = client.patch('/api/me', data=payload, format='json')

        self.assertEquals(request.status_code, 403)

        # Attempt to log in with old password (not changed)
        login_request = client.post('/api/auth', data={'email': user.email, 'password': 'ohyeah'}, format='json')

        self.assertEquals(login_request.status_code, 201)

    def test_me_view_set_patch_sanitize_successful(self):
        """
        Test that payload is sanitized (PK doesn't change)

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test2@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'id': 222,
            'age': 22
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data

        self.assertEquals(result['age'], 22)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.id, user.id)
        self.assertEquals(updated_user.age, 22)

    def test_me_view_set_patch_sanitize_uneditable(self):
        """
        Test that payload is sanitized (cannot change superuser status, etc)

        :return: None
        """
        # Create data
        user = account_models.User.objects.create_user(age=23, email='test@test.com', social_name='aeon',
                                                       username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'age': 22,
            'is_active': False,
            'is_admin': True,
            'is_superuser': True,
        }

        request = client.patch('/api/me', data=payload, format='json')
        result = request.data

        self.assertEquals(result['age'], 22)

        # Also check entry
        updated_user = account_models.User.objects.get(id=user.id)

        self.assertEquals(updated_user.age, 22)
        self.assertEquals(updated_user.is_active, True)
        self.assertEquals(updated_user.is_admin, False)
        self.assertEquals(updated_user.is_superuser, False)
