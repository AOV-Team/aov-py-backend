from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient
from unittest import skip


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

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)
        self.assertGreater(results[0]['id'], results[1]['id'])

    @skip('disabled')
    def test_photo_feed_photos_view_set_get_limited(self):
        """
        Test that we can limit number of results returned

        :return: None
        """
        # Create test data
        user = account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Landscape', photo_limit=4)
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.photo_feed = [feed]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.photo_feed = [feed]
        photo2.save()

        photo3 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo3.save()
        photo3.category = [category]
        photo3.photo_feed = [feed]
        photo3.save()

        photo4 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo4.save()
        photo4.category = [category]
        photo4.photo_feed = [feed]
        photo4.save()

        photo5 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo5.save()
        photo5.category = [category]
        photo5.photo_feed = [feed]
        photo5.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds/{}/photos'.format(feed.id))
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 4)

    @skip('disabled')
    def test_photo_feed_photos_view_set_get_random_limited(self):
        """
        Test that we can get a random list of photos for a feed

        :return: None
        """
        # Create test data
        user = account_models.User.objects\
            .create_user(email='mrtest@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov1')
        feed = photo_models.PhotoFeed.objects.create_or_update(name='Landscape', photo_limit=6, randomize=True)
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Test', classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.photo_feed = [feed]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo2.save()
        photo2.category = [category]
        photo2.photo_feed = [feed]
        photo2.save()

        photo3 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo3.save()
        photo3.category = [category]
        photo3.photo_feed = [feed]
        photo3.save()

        photo4 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo4.save()
        photo4.category = [category]
        photo4.photo_feed = [feed]
        photo4.save()

        photo5 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo5.save()
        photo5.category = [category]
        photo5.photo_feed = [feed]
        photo5.save()

        photo6 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo6.save()
        photo6.category = [category]
        photo6.photo_feed = [feed]
        photo6.save()

        photo7 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')), user=user)
        photo7.save()
        photo7.category = [category]
        photo7.photo_feed = [feed]
        photo7.save()

        access_user = account_models.User.objects \
            .create_user(email='mr@mypapaya.io', password='WhoWantsToBeAMillionaire?', username='aov2')

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_feeds/{}/photos'.format(feed.id))
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 6)

        # Check for randomness
        is_random = list()
        previous_id = 0

        for result in results:
            if not result['id'] == previous_id + 1:
                is_random.append(result)

            previous_id += 1

        if len(is_random) == 0:
            self.fail('Not random photos!')

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
