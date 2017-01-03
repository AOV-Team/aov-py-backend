from apps.account import models as account_models
from apps.common.models import get_date_stamp_str
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import override_settings, TestCase
from os.path import getsize
from rest_framework.test import APIClient
import re
import time


class TestPhotoViewSetGET(TestCase):
    """
    Test GET api/photos
    """
    def test_photo_view_set_get_successful(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear = [gear_1, gear_2]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertIn('next', request.data)
        self.assertEquals(len(results), 2)
        self.assertEquals(len(results[0]['gear']), 0)
        self.assertEquals(len(results[1]['gear']), 2)
        self.assertEquals(results[1]['gear'][0], gear_1.id)
        self.assertEquals(results[1]['latitude'], 43.0)
        self.assertEquals(results[1]['longitude'], -116.0)

    def test_photo_view_set_get_public(self):
        """
        Test that we get public photos

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), public=False, user=user)
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos')
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_view_set_get_classification(self):
        """
        Test that we get photos filtered by category

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?classification=night')
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_view_set_get_classification_does_not_exist(self):
        """
        Test that we get empty result set if classification does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

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

        request = client.get('/api/photos?classification=other')
        results = request.data['results']

        self.assertEquals(len(results), 0)

    def test_photo_view_set_get_classification_id(self):
        """
        Test that we get photos filtered by category (using ID)

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photos?classification={}'.format(category.id))
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_view_set_get_filtered(self):
        """
        Test that we get photos filtered by category and location

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   location='Boise', user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                   location='Boise', user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?classification=night&location=boise')
        results = request.data['results']

        self.assertEquals(len(results), 1)

    def test_photo_view_set_get_geo_location(self):
        """
        Test that we get photos filtered by a box of coordinates

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   location='boise', user=user)
        photo1.geo_location = 'POINT (-116.21 43.62)'
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.geo_location = 'POINT (-116.25 43.61699)'
        photo2.save()

        photo3 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo3.geo_location = 'POINT (-118.25 45.61699)'
        photo3.save()

        photo4 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo4.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=-118,42,-115,44')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_view_set_get_geo_missing_coordinate(self):
        """
        Test that we get 400 if geo_location is not properly formatted (missing a coord)

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=-118,42,-115')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_get_geo_bad_type(self):
        """
        Test that we get 400 if geo_location is a string

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?geo_location=a,b,c,d')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_get_location(self):
        """
        Test that we get photos filtered by location

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo1 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   location='boise', user=user)
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Case insensitive
        request = client.get('/api/photos?location=Boise')
        results = request.data['results']

        self.assertEquals(len(results), 1)


class TestPhotoViewSetPOST(TestCase):
    """
    Test POST api/photos
    """
    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_successful(self):
        """
        Test that we can save a photo.
        Saves locally.

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'geo_location': 'POINT ({} {})'.format(-116.2023436, 43.6169233),
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(result['user'], user.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['latitude'], 43.6169233)
        self.assertEquals(result['longitude'], -116.2023436)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)
        self.assertIsNotNone(photos[0].original_image_url)

        # Test that original uploaded image is saved (before resized and compressed)
        matched_images = test_helpers.find_file_by_pattern(settings.MEDIA_ROOT, '*_md-portrait.jpg')
        original_image = matched_images[0] if matched_images is not None else matched_images

        if original_image is not None:
            if not re.match('^u{}_'.format(user.id) + get_date_stamp_str().split('_')[0] + '_[0-9]{6}_md-portrait\.jpg$',
                            original_image):
                self.fail('Original image not matched!')
        else:
            self.fail('Original image not found!')

        # Sleep so other image-related unit tests don't get jacked up
        time.sleep(1)

        # Test that compression worked
        self.assertGreater(getsize(image), getsize('{}/{}'.format(settings.MEDIA_ROOT, str(photos[0].image))))

    def test_photo_view_set_post_remote_successful(self):
        """
        Test that we can save a photo. Must save remotely.

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/md-portrait.jpg'

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Landscape', classification_type='category')

        # Gear
        gear_1 = account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'gear': [gear_1.id, gear_2.id],
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        result = request.data

        self.assertEquals(result['category'][0], category.id)
        self.assertEquals(len(result['gear']), 2)
        self.assertEquals(result['user'], user.id)
        self.assertNotIn('original_image_url', result)

        # Query for entry
        photos = photo_models.Photo.objects.all()

        self.assertEquals(len(photos), 1)
        self.assertTrue(photos[0].public)

    @override_settings(REMOTE_IMAGE_STORAGE=False,
                       DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_photo_view_set_post_bad_geo_location(self):
        """
        Test that we get a 403 if geo_location is not in "POINT (long, lat)" format

        :return: None
        """
        # Test data
        image = 'apps/common/test/data/photos/cover.jpg'

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open(image, 'rb') as i:
            payload = {
                'category': category.id,
                'geo_location': '{} {}'.format(-116.2023436, 43.6169233),
                'image': i
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_post_bad_request_fields_missing(self):
        """
        Test that we get 400 if required fields are missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'image': image
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)

    def test_photo_view_set_post_bad_request_image_missing(self):
        """
        Test that we get 400 if image missing

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Landscape', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        with open('apps/common/test/data/photos/photo1-min.jpg', 'rb') as image:
            payload = {
                'category': category
            }

            request = client.post('/api/photos', data=payload, format='multipart')

        self.assertEquals(request.status_code, 400)
