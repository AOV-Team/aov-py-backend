from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoFeedPhotosViewSetGET(TestCase):
    """
    Test /api/photo_feeds/{}/photos
    """
    def test_photo_feed_photos_view_set_get_successful(self):
        """
        Test that we can get list of photos in a feed

        :return: None
        """
        # Create test data
        user = account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.photo_feed = [feed]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.photo_feed = [feed]
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds/{}/photos'.format(feed.id))
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_feed_photos_view_set_get_public(self):
        """
        Test that we can get list of PUBLIC photos in a feed

        :return: None
        """
        # Create test data
        user = account_models.User.objects \
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Landscape')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.photo_feed = [feed]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user, public=False)
        photo2.save()
        photo2.category = [category]
        photo2.photo_feed = [feed]
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds/{}/photos'.format(feed.id))
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_feed_photos_view_set_get_not_found(self):
        """
        Test that we get 404 if photo feed does not exist

        :return: None
        """
        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds/{}/photos'.format(55555))

        self.assertEquals(request.status_code, 404)
