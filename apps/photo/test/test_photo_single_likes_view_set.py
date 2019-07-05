from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleLikesViewSetDELETE(TestCase):
    """
    Test /api/photos/{}/likes
    """
    def test_photo_single_likes_view_set_delete_successful(self):
        """
        Test that we can delete a "like"

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.set([category])
        photo2.save()

        account_models.UserInterest.objects.create(content_object=photo1, user=user, interest_type='like')
        account_models.UserInterest.objects.create(content_object=photo2, user=user, interest_type='like')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/likes'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo2.id)

    def test_photo_single_likes_view_set_delete_bad_interest(self):
        """
        Test that we get 400 if user interest does not exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/randoms'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

    def test_photo_single_likes_view_set_delete_not_found(self):
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
        photo1.category.set([category])
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}/likes'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

    def test_photo_single_likes_view_set_delete_photo_not_found(self):
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

        request = client.delete('/api/photos/{}/likes'.format(5555), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)


class TestPhotoSingleLikesViewSetPOST(TestCase):
    """
    Test POST /api/photos/{}/likes
    """
    def test_photo_single_likes_view_set_post_successful(self):
        """
        Test that we can create a "like" for a photo

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.set([category])
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/photos/{}/likes'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 201)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo1.id)

    def test_photo_single_likes_view_set_post_bad_interest(self):
        """
        Test that we get 404 if user interest does not exist

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/photos/{}/randoms'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

    def test_photo_single_likes_view_set_post_duplicate(self):
        """
        Test that we get 409 if a like already exists

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/photos/{}/likes'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 201)

        # Second request
        request = client.post('/api/photos/{}/likes'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 409)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 1)
        self.assertEquals(interests[0].object_id, photo1.id)

    def test_photo_single_likes_view_set_post_photo_not_found(self):
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

        request = client.post('/api/photos/{}/likes'.format(4444), format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)
