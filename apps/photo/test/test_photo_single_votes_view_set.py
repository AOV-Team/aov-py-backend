from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleVotesViewSetPATCH(TestCase):
    """
    Test /api/photos/{}/votes
    """
    def test_photo_single_votes_view_set_increment_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.create_user(email="mrtest@mypapaya.io", password="pass", username="aov_hov")
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name="Test", classification_type="category")

        photo1 = photo_models \
            .Photo(image=Photo(open("apps/common/test/data/photos/photo1-min.jpg", "rb")), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        # Make a patch request to update the photo
        data = {
            "operation": "increment"
        }

        self.assertEqual(photo1.votes, 0)

        response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
        result = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["votes"], 1)

    def test_photo_single_votes_view_set_decrement_from_zero_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.create_user(email="mrtest@mypapaya.io", password="pass", username="aov_hov")
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name="Test", classification_type="category")

        photo1 = photo_models \
            .Photo(image=Photo(open("apps/common/test/data/photos/photo1-min.jpg", "rb")), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        # Make a patch request to update the photo
        data = {
            "operation": "decrement"
        }

        self.assertEqual(photo1.votes, 0)

        response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
        result = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["votes"], -1)

    def test_photo_single_votes_view_set_decrement_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.create_user(email="mrtest@mypapaya.io", password="pass", username="aov_hov")
        category = photo_models.PhotoClassification.objects \
            .create_or_update(name="Test", classification_type="category")

        photo1 = photo_models \
            .Photo(image=Photo(open("apps/common/test/data/photos/photo1-min.jpg", "rb")), user=user)
        photo1.save()
        photo1.category = [category]
        photo1.votes = 1
        photo1.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        # Make a patch request to update the photo
        data = {
            "operation": "decrement"
        }

        self.assertEqual(photo1.votes, 1)

        response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
        result = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["votes"], 0)
