from apps.account import models as account_models
from django.test import TestCase


class TestPhotoSingleInterestsViewSetDELETE(TestCase):
    """
    Test /api/photos/{}/interests
    """
    def test_photo_single_interests_view_set_delete_successful(self):
        """
        Test that we can delete a "star"

        :return: None
        """

    def test_photo_single_interests_view_set_delete_not_found(self):
        """
        Test that we get 404 if interest does not exist for the user

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
