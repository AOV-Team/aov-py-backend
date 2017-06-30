from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserFollowingViewSetGET(TestCase):
    def test_user_following_view_set_get_successful(self):
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
        target_user.follower.add(access_user)
        target_user.save()
        user_1.follower.add(access_user)
        user_1.save()
        user_2.follower.add(access_user)
        user_2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/following'.format(access_user.id), format='json')
        results = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertIn('count', request.data)
        self.assertIn('next', request.data)
        self.assertEquals(len(results), 3)
        self.assertEquals(results[0]['id'], user_2.id)
