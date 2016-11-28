from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoFeedViewSetGET(TestCase):
    """
    Test /api/photo_feeds
    """
    def test_photo_feed_view_set_get_successful(self):
        """
        Test that we can get list of photo feeds

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        photo_models.PhotoFeed.objects.create_or_update(name='Other')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_feed_view_set_get_public_only(self):
        """
        Test that we can get list of public photo feeds

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        photo_models.PhotoFeed.objects.create_or_update(name='Other')
        photo_models.PhotoFeed.objects.create_or_update(name='Misc', public=False)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds')
        results = request.data['results']

        self.assertEquals(len(results), 2)
