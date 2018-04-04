from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleCaptionViewSetPATCH(TestCase):
    def setUp(self):
        """
            Set up the needed data for the tests.

        :return: No return
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

    def tearDown(self):
        """
            Remove the test data after each round

        :return: No return
        """
        User.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')

    def test_photo_single_caption_view_set_patch_successful(self):
        """
        Test that updating the caption works

        :return: None
        """

        user = User.objects.get(email='test@aov.com')

        photo = photo_models.Photo.objects.get(user=user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {
            'caption': 'Adding a caption.'
        }

        request = client.patch('/api/photos/{}/caption'.format(photo.id), payload)

        self.assertEquals(request.status_code, 200)

        # Check db
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEqual(updated_photo.caption, payload['caption'])

    def test_photo_single_caption_view_set_patch_with_tags_successful(self):
        """
            Unit test to verify submitting a caption with tags correctly creates the tags

        :return: No return
        """

        user = User.objects.get(email="test@aov.com")
        photo = photo_models.Photo.objects.get(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {
            'caption': 'Adding a caption.',
            'tags': ["#Pretty", "#Boise", "#Personal"]
        }

        request = client.patch('/api/photos/{}/caption'.format(photo.id), payload)

        self.assertEquals(request.status_code, 200)

        # Check db
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEqual(updated_photo.caption, payload['caption'])
        self.assertEqual(updated_photo.tag.count(), 3)

    def test_photo_single_caption_view_set_patch_with_tags_no_hash_successful(self):
        """
            Unit test to see if tags submitted with no hashtag still work

        :return: No return
        """
        user = User.objects.get(email="test@aov.com")
        photo = photo_models.Photo.objects.get(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {
            'caption': 'Adding a caption.',
            'tags': ["Pretty", "Boise", "Personal"]
        }

        request = client.patch('/api/photos/{}/caption'.format(photo.id), payload)

        self.assertEquals(request.status_code, 200)

        # Check db
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEqual(updated_photo.caption, payload['caption'])
        self.assertEqual(updated_photo.tag.count(), 3)

    def test_photo_single_caption_view_set_patch_with_duplicate_tags_successful(self):
        """
            Unit test to verify that only one of any tag can be applied to a photo

        :return: No return
        """

        user = User.objects.get(email="test@aov.com")
        photo = photo_models.Photo.objects.get(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {
            'caption': 'Adding a caption.',
            'tags': ["Pretty", "Boise", "Personal", "Pretty Good", "Boise"]
        }

        request = client.patch('/api/photos/{}/caption'.format(photo.id), payload)

        self.assertEquals(request.status_code, 200)

        # Check db
        updated_photo = photo_models.Photo.objects.get(id=photo.id)

        self.assertEqual(updated_photo.caption, payload['caption'])
        self.assertEqual(updated_photo.tag.count(), 4)
