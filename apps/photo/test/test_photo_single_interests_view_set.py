from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleInterestsViewSetDELETE(TestCase):
    """
    Test /api/photos/{}/interests
    """
    def test_photo_single_interests_view_set_delete_successful(self):
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



        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.delete('/api/photos/{}'.format(photo1.id), format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        interests = account_models.UserInterest.objects.all()

        self.assertEquals(len(interests), 0)

    def test_photo_single_interests_view_set_delete_not_found(self):
        """
        Test that we get 200 if interest does not exist for the user

        :return: None
        """

    def test_photo_single_interests_view_set_delete_photo_not_found(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """


class TestPhotoSingleInterestsViewSetGET(TestCase):
    """
    Test GET /api/photos/{}/interests
    """
    def test_photo_single_interests_view_set_get_successful(self):
        """
        Test that we can get all "stars" for a photo

        :return: None
        """

    def test_photo_single_interests_view_set_get_none(self):
        """
        Test that we can get empty array if no stars

        :return: None
        """

    def test_photo_single_interests_view_set_get_photo_not_found(self):
        """
        Test that we get HTTP 404 if photo does not exist

        :return: None
        """


class TestPhotoSingleInterestsViewSetPOST(TestCase):
    """
    Test POST /api/photos/{}/interests
    """
    def test_photo_single_interests_view_set_post_successful(self):
        """
        Test that we can create a "star" for a photo

        :return: None
        """

    def test_photo_single_interests_view_set_post_photo_not_found(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """
