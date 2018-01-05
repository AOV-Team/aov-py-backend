from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoAppTopPhotosViewSetGET(TestCase):
    """
    Test GET /api/photos/top
    """
    def test_get_top_photos_successful(self):
        """
        Test that we can get photos for a classification

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects.create_or_update(
            name='night', classification_type='category')

        photo1 = photo_models.Photo(
            image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.add(classification)
        photo1.votes = 3
        photo1.save()

        photo2 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.add(classification)
        photo2.votes = 12
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/top'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 2)
        self.assertEqual(results[0]["id"], photo2.id)

    def test_get_aov_picks_successful(self):
        """
        Test that we can get photos for a classification

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects\
            .create_or_update(name='night', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.add(classification)
        photo1.votes = 89
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create(name="AOV Picks"))
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.add(classification)
        photo2.votes = 24
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/top?display_tab=picks'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEqual(results[0]["id"], photo1.id)