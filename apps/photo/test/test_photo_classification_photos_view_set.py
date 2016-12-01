from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoClassificationPhotosViewSetGET(TestCase):
    """
    Test GET /api/photo_classifications/{}/photos
    """
    def test_photo_classification_photos_view_set_get_successful(self):
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
        photo1.category = [classification]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [classification]
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications/{}/photos'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_classification_photos_view_set_get_public(self):
        """
        Test that we get public photos for a classification

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects \
            .create_or_update(name='night', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), public=False, user=user)
        photo1.save()
        photo1.category = [classification]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [classification]
        photo2.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications/{}/photos'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_classification_photos_view_set_get_not_found(self):
        """
        Test that we get 404 for classification that doesn't exist

        :return: None
        """
        # Test data
        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications/{}/photos'.format(55555))

        self.assertEquals(request.status_code, 404)
