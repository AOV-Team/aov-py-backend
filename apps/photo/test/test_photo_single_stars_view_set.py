from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import APNSDevice, PushNotificationRecord
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest import mock


class TestPhotoSingleStarsViewSetDELETE(TestCase):
    """
    Test /api/photos/{}/interests
    """
    def test_photo_single_stars_view_set_delete_successful(self):
        """
        Test that we can delete a "star"

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.save()

        account_models.UserInterest.objects.create(content_object=photo1, user=user, interest_type='star')
        account_models.UserInterest.objects.create(content_object=photo2, user=user, interest_type='star')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/stars'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo2.id)

    def test_photo_single_stars_view_set_delete_not_found(self):
        """
        Test that we get 200 if interest does not exist for the user

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/stars'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

    def test_photo_single_stars_view_set_delete_photo_not_found(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/stars'.format(5555), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestPhotoSingleStarsViewSetPOST(TestCase):
    """
    Test POST /api/photos/{}/interests
    """
    def test_photo_single_stars_view_set_post_successful(self):
        """
        Test that we can create a "star" for a photo

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        photo_owner = account_models.User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=photo_owner)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=photo_owner)
        photo2.save()
        photo2.category = [category]
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)


        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            # Get data from endpoint
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/photos/{}/stars'.format(photo1.id), format='json')

            self.assertEquals(request.status_code, 201)
            p.assert_called_with(
                alert="Your artwork has been saved by another user, {}.".format(photo_owner.username),
                registration_ids=[device.registration_id])

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo1.id)

        photos = client.get('/api/photos/{}'.format(photo1.id))

        self.assertTrue(photos.data["user_starred"]["starred"])

    def test_photo_single_stars_view_set_post_no_apns_device(self):
        """
            Unit test to make sure the endpoint still functions correctly even if push notifications fail

        :return: No return
        """

        user = account_models.User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo_owner = account_models.User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            request = client.post('/api/photos/{}/stars'.format(photo.id), format="json")

            self.assertEquals(request.status_code, 201)
            p.assert_not_called()

            # Check for entry
            interests = account_models.UserInterest.objects.all()

            self.assertEquals(len(interests), 1)
            self.assertEquals(interests[0].object_id, photo.id)

            photos = client.get('/api/photos/{}'.format(photo.id))

            self.assertTrue(photos.data["user_starred"]["starred"])

    def test_photo_single_stars_view_set_post_duplicate(self):
        """
        Test that we get 409 if star already exists

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        photo_owner = account_models.User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=photo_owner)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            # Get data from endpoint
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/photos/{}/stars'.format(photo1.id), format='json')

            self.assertEquals(request.status_code, 201)
            p.assert_called_with(
                alert="Your artwork has been saved by another user, {}.".format(photo_owner.username),
                registration_ids=[device.registration_id])

            # Second request
            request = client.post('/api/photos/{}/stars'.format(photo1.id), format='json')

            self.assertEquals(request.status_code, 409)
            p.assert_called_once_with(
                alert="Your artwork has been saved by another user, {}.".format(photo_owner.username),
                registration_ids=[device.registration_id])

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo1.id)

    def test_photo_single_stars_view_set_post_photo_not_found(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            # Get data from endpoint
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + token)

            request = client.post('/api/photos/{}/stars'.format(4444), format='json')

            self.assertEquals(request.status_code, 404)
            p.assert_not_called()

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)
