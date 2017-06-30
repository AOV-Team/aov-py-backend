from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleCaptionViewSetPATCH(TestCase):
    def test_photo_single_caption_view_set_patch_successful(self):
        """
        Test that updating the caption works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

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