from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from apps.utils.models import UserAction
from datetime import timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
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

        request = client.get('/api/photos/top?display_page=picks'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 1)
        self.assertEqual(results[0]["id"], photo1.id)
        
    def test_get_popular_successful(self):
        """
            Unit test to validate then when requesting images for the popular feed, they return in order of most clicked
        
        :return: No return
        """

        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects \
            .create_or_update(name='night', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.add(classification)
        photo1.votes = 89
        photo1.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.add(classification)
        photo2.votes = 24
        photo2.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)

        photo3 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo3.save()
        photo3.category.add(classification)
        photo3.votes = 179
        photo3.created_at = timezone.now() - timedelta(days=32)
        photo3.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/top?display_page=popular'.format(classification.id))
        results = request.data['results']

        self.assertEquals(len(results), 2)
        self.assertEqual(results[0]["id"], photo2.id)


    @override_settings(REMOTE_IMAGE_STORAGE=False)
    def test_aov_web_all_successful(self):
        """
        Unit test to verify aov_web_image page can be retrieved, correctly ordered

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects.create_or_update(
            name='night', classification_type='category')

        photo1 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.add(classification)
        photo1.votes = 89
        photo1.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        photo_models.PhotoComment.objects.create_or_update(photo=photo1, comment="Yep, cool dude.", user=user)

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.add(classification)
        photo2.votes = 24
        photo2.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)

        photo3 = photo_models.Photo(
            image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo3.save()
        photo3.category.add(classification)
        photo3.votes = 179
        photo3.created_at = timezone.now() - timedelta(days=32)
        photo3.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)

        access_user = account_models.User.objects.create_user(
            email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/top?display_page=aov-web-all')
        results = request.data['results']

        self.assertEquals(len(results), 3)
        self.assertEqual(results[0]["id"], photo3.id)
        self.assertEqual(results[1]["id"], photo1.id)

    @override_settings(REMOTE_IMAGE_STORAGE=False)
    def test_aov_web_weekly_successful(self):
        """
        Unit test to verify aov_web_image page can be retrieved, correctly ordered

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        classification = photo_models.PhotoClassification.objects.create_or_update(
            name='night', classification_type='category')

        photo1 = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category.add(classification)
        photo1.votes = 89
        photo1.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo1)
        photo_models.PhotoComment.objects.create_or_update(photo=photo1, comment="Yep, cool dude.", user=user)

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category.add(classification)
        photo2.votes = 24
        photo2.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo2)

        photo3 = photo_models.Photo(
            image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo3.save()
        photo3.category.add(classification)
        photo3.votes = 179
        photo3.created_at = timezone.now() - timedelta(days=32)
        photo3.save()
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)
        UserAction.objects.create(user=user, action='photo_click', content_object=photo3)

        access_user = account_models.User.objects.create_user(
            email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos/top?display_page=aov-web-weekly')
        results = request.data['results']

        self.assertEquals(len(results), 2)
        self.assertEqual(results[0]["id"], photo1.id)
        self.assertEqual(results[1]["id"], photo2.id)
