from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserStarsViewSetDELETE(TestCase):
    """
    Test DELETE /api/users/{}/stars
    """
    def test_user_stars_view_set_delete_successful(self):
        """
        Test that we can unstar a user

        :return: None
        """
        # Test data
        random_user = account_models.User.objects.create_user(email='rr@mypapaya.io', social_name='@random',
                                                              username='r')
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')
        account_models.UserInterest.objects.create(content_object=random_user, user=user, interest_type='star')
        account_models.UserInterest.objects.create(content_object=target_user, user=user, interest_type='star')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/stars'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, random_user.id)

    def test_user_stars_view_set_delete_no_star(self):
        """
        Test that we still get HTTP 200 if user was not being followed

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/stars'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 200)

    def test_user_stars_view_set_delete_user_does_not_exist(self):
        """
        Test that we get 404 if user does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/stars'.format(5555), format='json')

        self.assertEquals(request.status_code, 404)


class TestUserStarsViewSetPOST(TestCase):
    """
    Test POST /api/users/{}/stars
    """
    def test_user_stars_view_set_post_successful(self):
        """
        Test that we can star a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/stars'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 201)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)

    def test_user_stars_view_set_post_duplicate(self):
        """
        Test that we cannot create more than one star for a user
        Expect 409

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/stars'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 201)

        # Second time
        request = client.post('/api/users/{}/stars'.format(target_user.id), format='json')

        self.assertEquals(request.status_code, 409)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)

    def test_user_stars_view_set_post_user_does_not_exist(self):
        """
        Test that we get 404 if user does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/users/{}/stars'.format(555), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)
