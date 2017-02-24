from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


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
        account_models.UserInterest.objects.create(content_object=target_user, user=user_1, interest_type='follow')
        account_models.UserInterest.objects.create(content_object=target_user, user=user_2, interest_type='follow')

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

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 2)

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
        account_models.UserInterest.objects.create(content_object=target_user, user=user_1, interest_type='follow')
        account_models.UserInterest.objects.create(content_object=target_user, user=user_2, interest_type='follow')

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

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 2)

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
        account_models.UserInterest.objects.create(content_object=target_user, user=user_1, interest_type='follow')
        account_models.UserInterest.objects.create(content_object=target_user, user=user_2, interest_type='follow')

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

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 2)


class TestUserFollowersViewSetPOST(TestCase):
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

        # Follow target user
        account_models.UserInterest.objects.create(content_object=target_user, user=user_1, interest_type='follow')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 201)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 2)

        for interest in interests:
            if interest.user.id != access_user.id and interest.user.id != user_1.id:
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
        account_models.UserInterest.objects.create(content_object=target_user, user=access_user, interest_type='follow')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/followers'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 409)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)

        interest = interests.first()

        self.assertEquals(interest.user.id, access_user.id)

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
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)
