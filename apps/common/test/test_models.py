from apps.account import models as account_models
from apps.photo import models as photo_models
from apps.common import models as common_models
from django.test import TestCase
import re


class TestGetUploadedFilePath(TestCase):
    """
    Test file naming
    """
    def test_get_uploaded_file_path_successful(self):
        """
        Test that file naming is correct

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        photo = photo_models.Photo(user=user)

        image_path = common_models.get_uploaded_file_path(photo, 'photo.jpg')

        if not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{6}_u' + str(user.id) + '\.jpg', image_path):
            self.fail()

    def test_get_uploaded_file_path_no_user(self):
        """
        Test that file naming is correct even if no user

        :return: None
        """
        # Test data
        photo = photo_models.Photo()

        image_path = common_models.get_uploaded_file_path(photo, 'photo.jpg')

        if not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{6}_photo\.jpg$',
                        image_path):
            self.fail()
