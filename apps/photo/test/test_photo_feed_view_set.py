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
        photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        photo_models.PhotoFeed.objects.create_or_update(name='Other')

        # Log user in
        client = APIClient()

        request = client.get('/api/photo_feeds')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_feed_view_set_get_public_only(self):
        """
        Test that we can get list of public photo feeds

        :return: None
        """
        # Create test data
        photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        photo_models.PhotoFeed.objects.create_or_update(name='Other')
        photo_models.PhotoFeed.objects.create_or_update(name='Misc', public=False)

        # Log user in
        client = APIClient()

        request = client.get('/api/photo_feeds')
        results = request.data['results']

        self.assertEquals(len(results), 2)
