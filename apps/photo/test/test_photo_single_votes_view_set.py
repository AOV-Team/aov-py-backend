from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import APNSDevice, PushNotificationRecord
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase
from fcm_django.models import FCMDevice
from rest_framework.test import APIClient
from unittest import mock


class TestPhotoSingleVotesViewSetPATCH(TestCase):
    """
    Test /api/photos/{}/votes
    """
    def setUp(self):
        """
            Method to set up reused data for unit tests

        :return: None
        """
        # Create test data
        account_models.User.objects.create_user(email="mrtest@mypapaya.io", password="pass", username="aov_hov")
        photo_owner = account_models.User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        category = photo_models.PhotoClassification.objects.create_or_update(
            name="Test", classification_type="category")

        photo1 = photo_models.Photo(image=Photo(open("apps/common/test/data/photos/photo1-min.jpg", "rb")),
                                    user=photo_owner)
        photo1.save()
        photo1.category.set([category])
        photo1.save()

        FCMDevice.objects.create(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50',
                                 user=photo_owner)


    def tearDown(self):
        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        photo_models.PhotoVote.objects.all().delete()
        PushNotificationRecord.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')
        FCMDevice.objects.all().delete()

    def test_photo_single_votes_view_set_increment_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.get(username="aov_hov")
        photo_owner = account_models.User.objects.get(username="aov1")

        photo1 = photo_models.Photo.objects.filter(user=photo_owner).first()

        device = FCMDevice.objects.get(user=photo_owner)

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

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
            result = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(result["votes"], 1)
            p.assert_called_with(api_key=None, badge=None, data=None, icon=None, sound=None, title=None,
                                 body="{} has upvoted your artwork, {}.".format(user.username, photo_owner.username),
                                 registration_ids=[device.registration_id])

        self.assertEqual(PushNotificationRecord.objects.count(), 1)
        # Check for the new PhotoVote entry
        photo_vote = photo_models.PhotoVote.objects.filter(photo=photo1, user=user)
        self.assertTrue(photo_vote.exists())
        self.assertTrue(photo_vote.first().upvote)


    def test_photo_single_votes_view_set_increment_patch_successful_no_device(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.get(username="aov_hov")
        photo_owner = account_models.User.objects.get(username="aov1")
        photo1 = photo_models.Photo.objects.filter(user=photo_owner).first()
        FCMDevice.objects.all().delete()

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

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
            result = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(result["votes"], 1)
            p.assert_not_called()

        self.assertEqual(PushNotificationRecord.objects.count(), 0)
        # Check for the new PhotoVote entry
        photo_vote = photo_models.PhotoVote.objects.filter(photo=photo1, user=user)
        self.assertTrue(photo_vote.exists())
        self.assertTrue(photo_vote.first().upvote)

    def test_photo_single_votes_view_set_decrement_from_zero_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.get(username="aov1")
        photo1 = photo_models.Photo.objects.filter(user=user).first()

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

        # Check for the new PhotoVote entry
        photo_vote = photo_models.PhotoVote.objects.filter(photo=photo1, user=user)
        self.assertTrue(photo_vote.exists())
        self.assertFalse(photo_vote.first().upvote)

    def test_photo_single_votes_view_set_decrement_patch_successful(self):
        """
        Test that we can do a partial update, allowing for incrementing of votes

        :return: None
        """

        # Create test data
        user = account_models.User.objects.get(username="aov1")
        photo1 = photo_models.Photo.objects.filter(user=user).first()
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

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            response = client.patch("/api/photos/{}/votes".format(photo1.id), data=data, format="json")
            result = response.data

            self.assertEqual(response.status_code, 200)
            self.assertEqual(result["votes"], 0)
            p.assert_not_called()

        self.assertEqual(PushNotificationRecord.objects.count(), 0)
        # Check for the new PhotoVote entry
        photo_vote = photo_models.PhotoVote.objects.filter(photo=photo1, user=user)
        self.assertTrue(photo_vote.exists())
        self.assertFalse(photo_vote.first().upvote)
