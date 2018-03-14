from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.communication.models import PushNotificationRecord
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase, override_settings
from push_notifications.models import APNSDevice
from rest_framework.test import APIClient
from unittest import mock
import uuid


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestPhotoSingleCommentViewSetPOST(TestCase):
    def setUp(self):
        """
            Sets up necessary base information for each test case

        :return: No return
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)

        APNSDevice.objects.create(registration_id=str(uuid.uuid4()).replace("-", ""), user=user)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        photo_models.PhotoComment.objects.create_or_update(photo=photo, user=photo_owner,
                                                           comment="Dude, sick photo! I dig it.")

    def tearDown(self):
        User.objects.all().delete()
        photo_models.PhotoComment.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')
        APNSDevice.objects.all().delete()

    def test_photo_single_comment_reply_view_set_post_successful(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.get(email='test@aov.com')
        photo_owner = User.objects.get(email="mr@aov.com")
        photo = photo_models.Photo.objects.get(user=photo_owner)
        photo_comment = photo_models.PhotoComment.objects.get(user=photo_owner)
        owner_device = APNSDevice.objects.get(user=photo_owner)
        user_device = APNSDevice.objects.get(user=user)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'reply': 'Thanks, man!'
            }

            request = client.post('/api/photos/{}/comments/{}/replies'.format(photo.id, photo_comment.id), payload)

            self.assertEquals(request.status_code, 201)
            p.assert_called_with(
                alert="{} has commented on your artwork, {}.".format(user.username, photo_owner.username),
                registration_ids=[owner_device.registration_id])

            p.assert_called_with(
                alert="{} has replied to your comment, {}.".format(photo_owner.username, user.username),
                registration_ids=[user_device.registration_id])

        # Check db
        new_comment = photo_models.PhotoComment.objects.first()

        self.assertEqual(PushNotificationRecord.objects.count(), 2)
        self.assertEqual(new_comment.comment, payload['reply'])
        self.assertEqual(new_comment.parent, photo_comment.id)
        self.assertEqual(new_comment.user.email, photo_owner.email)

    # def test_photo_single_comment_view_set_post_no_comment_text(self):
    #     """
    #         Test that posting a new comment works
    #
    #     :return: None
    #     """
    #
    #     user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
    #
    #     photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
    #                                user=user)
    #     photo.save()
    #
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))
    #
    #     payload = {}
    #
    #     request = client.post('/api/photos/{}/comments'.format(photo.id), payload)
    #
    #     self.assertEquals(request.status_code, 400)
    #     self.assertEqual(request.data["userMessage"], "A comment string cannot be empty.")
    #     self.assertEqual(request.data["message"], "Missing required field 'comment' in request data.")
    #
    # def test_photo_single_comment_view_set_post_not_authorized(self):
    #     """
    #         Test that posting a new comment works
    #
    #     :return: None
    #     """
    #
    #     user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
    #
    #     photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
    #                                user=user)
    #     photo.save()
    #
    #     client = APIClient()
    #
    #     payload = {}
    #
    #     request = client.post('/api/photos/{}/comments'.format(photo.id), payload)
    #
    #     self.assertEquals(request.status_code, 403)
