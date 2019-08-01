from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserFollowersViewSetDELETE(TestCase):
    def test_user_followers_view_set_delete_successful(self):
        """
        Test that we can stop following a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower.set([access_user, user_1])
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/followers/{}'.format(target_user.id, access_user.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(followers.count(), 1)

        follower = followers.first()

        self.assertEquals(follower.id, user_1.id)

    def test_user_followers_view_set_delete_not_following(self):
        """
        Test that we get a 200 if we aren't following this user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Follow target user
        target_user.follower.set([user_1])
        target_user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/followers/{}'.format(target_user.id, access_user.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(followers.count(), 1)

        follower = followers.first()

        self.assertEquals(follower.id, user_1.id)

    def test_user_followers_view_set_delete_not_found(self):
        """
        Test that we get HTTP 404 if user does not exist

        :return: None
        """
        # Test data
        access_user = account_models.User.objects.create_user(email='mr@aov.com', social_name='@mr', username='mr')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/users/{}/followers/{}'.format(9999, access_user.id), format='json')

        self.assertEquals(request.status_code, 404)

    def test_user_followers_view_set_delete_unauthenticated(self):
        """
        Test that we need to be logged in to delete a user

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')

        # Follow target user
        target_user.follower.set([user_1])
        target_user.save()

        # Get data from endpoint
        client = APIClient()

        request = client.delete('/api/users/{}/followers/{}'.format(target_user.id, 9999), format='json')

        self.assertEquals(request.status_code, 401)

        # Check for entry
        followers = target_user.follower.all()

        self.assertEquals(followers.count(), 1)

        follower = followers.first()

        self.assertEquals(follower.id, user_1.id)
