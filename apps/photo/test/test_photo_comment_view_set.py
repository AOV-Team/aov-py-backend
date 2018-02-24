from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.test import TestCase, override_settings
from push_notifications.models import APNSDevice
from rest_framework.test import APIClient
from unittest import mock


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
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=user)

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

        with mock.patch('push_notifications.apns.apns_send_bulk_message') as p:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

            payload = {
                'comment': 'Dude, sick photo! I dig it.'
            }

            request = client.post('/api/photos/{}/comments'.format(photo.id), payload)

            self.assertEquals(request.status_code, 201)
            p.assert_called_with(alert="{} has commented on your artwork.".format(user.username),
                                 registration_ids=[device.registration_id])

            # Check db
            new_comment = photo_models.PhotoComment.objects.first()

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
