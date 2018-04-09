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
class TestPhotoSingleCommentReplyViewSetPOST(TestCase):
    def setUp(self):
        """
            Sets up necessary base information for each test case

        :return: No return
        """

        commenter = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)

        APNSDevice.objects.create(registration_id=str(uuid.uuid4()).replace("-", ""), user=commenter)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        photo_models.PhotoComment.objects.create_or_update(photo=photo, user=commenter,
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
        photo_comment = photo_models.PhotoComment.objects.get(user=user)
        user_device = APNSDevice.objects.get(user=user)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(photo_owner))

            payload = {
                'reply': 'Thanks, man!'
            }

            request = client.post('/api/photos/{}/comments/{}/replies'.format(photo.id, photo_comment.id), payload)

            self.assertEquals(request.status_code, 201)

            p.assert_called_with(
                alert="{} replied to your comment, {}.".format(photo_owner.username, user.username),
                registration_ids=[user_device.registration_id])

        # Check db
        new_comment = photo_models.PhotoComment.objects.filter(parent__isnull=False).first()

        self.assertEqual(PushNotificationRecord.objects.count(), 1)
        self.assertEqual(new_comment.comment, payload['reply'])
        self.assertEqual(new_comment.parent.id, photo_comment.id)
        self.assertEqual(new_comment.user.email, photo_owner.email)

    def test_photo_single_comment_view_set_post_no_comment_text(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.get(username='testuser')
        photo_owner = User.objects.get(username='aov1')

        photo = photo_models.Photo.objects.get(user=photo_owner)

        photo_comment = photo_models.PhotoComment.objects.get(photo=photo)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {}

        request = client.post('/api/photos/{}/comments/{}/replies'.format(photo.id, photo_comment.id), payload)

        self.assertEquals(request.status_code, 400)
        self.assertEqual(request.data["userMessage"], "A comment string cannot be empty.")
        self.assertEqual(request.data["message"], "Missing required field 'comment' in request data.")

    def test_photo_single_comment_view_set_post_not_authorized(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.get(username='testuser')
        photo_owner = User.objects.get(username='aov1')

        photo = photo_models.Photo.objects.get(user=photo_owner)
        photo_comment = photo_models.PhotoComment.objects.get(photo=photo)

        client = APIClient()

        payload = {}

        request = client.post('/api/photos/{}/comments/{}/replies'.format(photo.id, photo_comment.id), payload)

        self.assertEquals(request.status_code, 403)

    def test_photo_single_comment_view_set_post_with_tagged_users(self):
        """
            Unit test to verify that providing a list of tagged users results in proper notifications being sent

        :return: No return value
        """
        # Create the further users for purpose of testing tagging
        user = User.objects.get(username="testuser")
        tagged_one = User.objects.create_user('test1@aov.com', 'testuser1', 'pass')
        tagged_two = User.objects.create_user('test2@aov.com', 'testuser2', 'pass')
        tagged_three = User.objects.create_user('test3@aov.com', 'testuser3', 'pass')
        photo_owner = User.objects.get(username="aov1")
        device = APNSDevice.objects.get(user=user)

        tagged_one_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_one)
        tagged_two_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_two)
        tagged_three_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_three)

        photo = photo_models.Photo.objects.get(user=photo_owner)
        photo_comment = photo_models.PhotoComment.objects.get(photo=photo)

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(photo_owner))

            payload = {
                'reply': 'Thanks!',
                'tagged': [tagged_one.username, tagged_two.username, tagged_three.username]
            }

            request = client.post('/api/photos/{}/comments/{}/replies'.format(photo.id, photo_comment.id), payload)

            self.assertEquals(request.status_code, 201)
            calls = list()
            calls.append(mock.call(
                alert="{} replied to your comment, {}.".format(photo_owner.username, user.username),
                registration_ids=[device.registration_id]))
            calls.append(mock.call(
                alert="{} tagged you in a comment, {}.".format(photo_owner.username, tagged_one.username),
                registration_ids=[tagged_one_device.registration_id]))
            calls.append(mock.call(
                alert="{} tagged you in a comment, {}.".format(photo_owner.username, tagged_two.username),
                registration_ids=[tagged_two_device.registration_id]))
            calls.append(mock.call(
                alert="{} tagged you in a comment, {}.".format(photo_owner.username, tagged_three.username),
                registration_ids=[tagged_three_device.registration_id]))

            p.assert_has_calls(calls=calls)

        # Check db
        new_comment = photo_models.PhotoComment.objects.filter(parent__isnull=False).first()

        self.assertEqual(PushNotificationRecord.objects.count(), 4)
        self.assertEqual(new_comment.comment, payload['reply'])
        self.assertEqual(len(new_comment.mentions), 3)
        self.assertEqual(new_comment.user.email, photo_owner.email)
