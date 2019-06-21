from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestUsersPhotosViewSetPOST(TestCase):
    """
    Test /api/users/{}/photos GET
    """
    def test_users_photos_view_set_get_successful(self):
        """
        Successful get users photos (newest first)
        /api/users/{}/photos

        :return: None
        """
        # Create user and data
        access_user = account_models.User.objects.create_user(email='m@mypapaya.io', password='pass', username='m')
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models\
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models\
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/photos'.format(user.id), format='json')
        result = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertEquals(len(result), 2)
        self.assertEquals(result[0]['id'], photo2.id)  # newest first
        self.assertIn('dimensions', result[0])
        self.assertIn('image_blurred', result[0])
        self.assertIn('image', result[0])

    def test_users_photos_view_set_get_no_photos(self):
        """
        Successful get response with no results
        /api/users/{}/photos

        :return: None
        """
        # Create user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/photos'.format(user.id), format='json')
        result = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertEquals(len(result), 0)

    def test_users_photos_view_set_get_no_user(self):
        """
        Test that we get HTTP 404 if user does not exist
        /api/users/{}/photos

        :return: None
        """
        # Create user
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/photos'.format(99999), format='json')

        self.assertEquals(request.status_code, 404)

    def test_users_photos_view_set_get_own_photos(self):
        """
        Successful get own user's photos (newest first)
        /api/users/{}/photos

        :return: None
        """
        # Create user and data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models\
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models\
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/users/{}/photos'.format(user.id), format='json')
        result = request.data['results']

        self.assertEquals(request.status_code, 200)
        self.assertEquals(len(result), 2)
        self.assertEquals(result[0]['id'], photo2.id)  # newest first
        self.assertIn('dimensions', result[0])
        self.assertIn('image_blurred', result[0])
        self.assertIn('image', result[0])
