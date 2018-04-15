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
    def test_photo_single_comment_view_set_post_successful(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'comment': 'Dude, sick photo! I dig it.'
            }

            request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

            self.assertEquals(request.status_code, 201)
            p.assert_called_with(
                alert="{} has commented on your artwork, {}.".format(user.username, photo_owner.username),
                registration_ids=[device.registration_id])

        # Check db
        new_comment = photo_models.PhotoComment.objects.first()

        self.assertEqual(PushNotificationRecord.objects.count(), 1)
        self.assertEqual(new_comment.comment, payload['comment'])
        self.assertEqual(new_comment.user.email, user.email)


    def test_photo_single_comment_view_set_post_no_apns_device(self):
        """
            Unit test to make sure the endpoint still functions correctly even if push notifications fail

        :return: No return
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'comment': 'Dude, sick photo! I dig it.'
            }

            request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

            self.assertEquals(request.status_code, 201)
            p.assert_not_called()

        # Check db
        new_comment = photo_models.PhotoComment.objects.first()

        self.assertEqual(PushNotificationRecord.objects.count(), 0)
        self.assertEqual(new_comment.comment, payload['comment'])
        self.assertEqual(new_comment.user.email, user.email)


    def test_photo_single_comment_view_set_post_no_comment_text(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=user)
        photo.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {}

        request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

        self.assertEquals(request.status_code, 400)
        self.assertEqual(request.data["userMessage"], "A comment string cannot be empty.")
        self.assertEqual(request.data["message"], "Missing required field 'comment' in request data.")

    def test_photo_single_comment_view_set_post_not_authorized(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=user)
        photo.save()

        client = APIClient()

        payload = {}

        request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

        self.assertEquals(request.status_code, 403)

    def test_photo_single_comment_view_set_post_with_tagged_users(self):
        """
            Unit test to verify that providing a list of tagged users results in proper notifications being sent

        :return: No return value
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        tagged_one = User.objects.create_user('test1@aov.com', 'testuser1', 'pass')
        tagged_two = User.objects.create_user('test2@aov.com', 'testuser2', 'pass')
        tagged_three = User.objects.create_user('test3@aov.com', 'testuser3', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)

        tagged_one_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_one)
        tagged_two_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_two)
        tagged_three_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_three)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'comment': 'Dude, sick photo! I dig it.',
                'mentions': [tagged_one.username, tagged_two.username, tagged_three.username]
            }

            request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

            self.assertEquals(request.status_code, 201)
            calls = list()
            calls.append(mock.call(
                alert="{} has commented on your artwork, {}.".format(user.username, photo_owner.username),
                registration_ids=[device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_one.username),
                registration_ids=[tagged_one_device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_two.username),
                registration_ids=[tagged_two_device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_three.username),
                registration_ids=[tagged_three_device.registration_id]))

            p.assert_has_calls(calls=calls)

        # Check db
        new_comment = photo_models.PhotoComment.objects.first()

        self.assertEqual(PushNotificationRecord.objects.count(), 4)
        self.assertEqual(new_comment.comment, payload['comment'])
        self.assertEqual(len(new_comment.mentions), 3)
        self.assertEqual(new_comment.user.email, user.email)

    def test_photo_single_comment_view_set_post_with_tagged_users_with_multiple_devices(self):
        """
            Unit test to verify that providing a list of tagged users results in proper notifications being sent

            *NOTE* This will likely fail as the order of the id's in the endpoint has no order

        :return: No return value
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')
        tagged_one = User.objects.create_user('test1@aov.com', 'testuser1', 'pass')
        tagged_two = User.objects.create_user('test2@aov.com', 'testuser2', 'pass')
        tagged_three = User.objects.create_user('test3@aov.com', 'testuser3', 'pass')
        photo_owner = User.objects.create_user(email="mr@aov.com", password="pass", username="aov1")
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=photo_owner)

        tagged_one_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_one)
        tagged_one_device_two = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_one)
        tagged_two_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_two)
        tagged_two_device_two = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_two)
        tagged_three_device = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_three)
        tagged_three_device_two = APNSDevice.objects.create(
            registration_id=str(uuid.uuid4()).replace("-", ""), user=tagged_three)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=photo_owner)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'comment': 'Dude, sick photo! I dig it.',
                'mentions': [tagged_one.username, tagged_two.username, tagged_three.username]
            }

            request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

            self.assertEquals(request.status_code, 201)
            calls = list()
            calls.append(mock.call(
                alert="{} has commented on your artwork, {}.".format(user.username, photo_owner.username),
                registration_ids=[device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_one.username),
                registration_ids=[tagged_one_device_two.registration_id, tagged_one_device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_two.username),
                registration_ids=[tagged_two_device_two.registration_id, tagged_two_device.registration_id]))
            calls.append(mock.call(
                alert="{} mentioned you in a comment, {}.".format(user.username, tagged_three.username),
                registration_ids=[tagged_three_device_two.registration_id, tagged_three_device.registration_id]))

            p.assert_has_calls(calls=calls)

        # Check db
        new_comment = photo_models.PhotoComment.objects.first()

        self.assertEqual(PushNotificationRecord.objects.count(), 4)
        self.assertEqual(new_comment.comment, payload['comment'])
        self.assertEqual(len(new_comment.mentions), 3)
        self.assertEqual(new_comment.user.email, user.email)


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestPhotoSingleCommentViewSetGET(TestCase):
    def test_photo_single_comment_view_set_get_successful(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        payload = {
            'comment': 'Dude, sick photo! I dig it.'
        }

        request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

        self.assertEquals(request.status_code, 201)

        second_payload = {
            'comment': 'Impressive.'
        }

        request = client.post('/api/photos/{}/comments'.format(photo.id), second_payload)

        self.assertEquals(request.status_code, 201)

        # Use a get request to retrieve the comment
        result = client.get('/api/photos/{}/comments'.format(photo.id))

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data["results"]), 2)
        self.assertEqual(result.data["results"][0]["comment"], second_payload["comment"])

    def test_photo_single_comment_view_set_get_no_comments(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=user)
        photo.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        # Use a get request to retrieve the comment
        result = client.get('/api/photos/{}/comments'.format(photo.id))

        self.assertEqual(result.status_code, 200)

    def test_photo_single_comment_view_set_get_not_authorized(self):
        """
            Test that posting a new comment works

        :return: None
        """

        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                   user=user)
        photo.save()

        client = APIClient()

        # Use a get request to retrieve the comment
        result = client.get('/api/photos/{}/comments'.format(photo.id))

        self.assertEquals(result.status_code, 403)
