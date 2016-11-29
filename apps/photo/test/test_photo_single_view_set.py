from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import PhotoFile
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleViewSetDELETE(TestCase):
    """
    Test POST /api/photos/{}
    """
    def test_photo_single_view_set_delete_successful(self):
        """
        Test that we can "delete" a photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}'.format(photo.id))

        self.assertEquals(request.status_code, 200)

        # Query for entry
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEquals(updated_photo.public, False)

    def test_photo_single_view_set_delete_forbidden(self):
        """
        Test that non-owner cannot "delete" a photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()

        access_user = account_models.User.objects.create_user(email='mr@mypapaya.io', password='Who?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}'.format(photo.id))

        self.assertEquals(request.status_code, 403)

        # Query for entry
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEquals(updated_photo.public, True)


class TestPhotoSingleViewSetGET(TestCase):
    """
    Test /api/photos/{}
    """
    def test_photo_single_view_set_get_successful(self):
        """
        Test that we can get a photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/{}'.format(photo.id))
        results = request.data

        self.assertEquals(results['user'], user.id)

    def test_photo_single_view_set_get_deleted(self):
        """
        Test that we get 404 if photo has been "deleted"

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), public=False, user=user)
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/{}'.format(photo.id))

        self.assertEquals(request.status_code, 404)

    def test_photo_single_view_set_get_does_not_exist(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/{}'.format(5555))

        self.assertEquals(request.status_code, 404)


class TestPhotoSingleViewSetPATCH(TestCase):
    """
    Test PATCH /api/photos/{}
    """
    def test_photo_single_view_set_patch_successful(self):
        """
        Test that we can update a photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_superuser(email='mrtest@mypapaya.io', password='WhoAmI')

        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Landscape', classification_type='category')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Night')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo.category = [category]
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'photo_feed': [feed.id],
        }

        request = client.patch('/api/photos/{}'.format(photo.id), data=payload, format='json')
        results = request.data

        self.assertEquals(results['photo_feed'], [feed.id])

        # Query for entry
        photos = photo_models.Photo.objects.filter(id=photo.id)

        self.assertEquals(len(photos), 1)
        self.assertEquals(photos[0].photo_feed.all()[0].id, feed.id)

    def test_photo_single_view_set_patch_not_superuser(self):
        """
        Test that regular user cannot update photo

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aovyy')

        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Landscape', classification_type='category')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Night')

        photo = photo_models \
            .Photo(image=PhotoFile(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo.category = [category]
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'photo_feed': [feed.id],
        }

        request = client.patch('/api/photos/{}'.format(photo.id), data=payload, format='json')

        self.assertEquals(request.status_code, 403)

        # Query for entry
        photos = photo_models.Photo.objects.filter(id=photo.id)

        self.assertEquals(len(photos), 1)
        self.assertEquals(len(photos[0].photo_feed.all()), 0)
