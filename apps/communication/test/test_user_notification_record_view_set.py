from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import APNSDevice, PushNotificationRecord
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from datetime import timedelta
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestUserNotificationRecordViewSetGET(TestCase):
    def setUp(self):
        """
            Set up for the test suite. To be ran in between each test

        :return: No return
        """
        client = APIClient()
        with open('apps/common/test/data/photos/cover.jpg', 'rb') as image:
            payload = {
                'age': 23,
                'avatar': image,
                'email': 'mrtest@mypapaya.io',
                'first_name': 'Martin',
                'last_name': 'Ronquillo',
                'location': 'Boise',
                'password': 'WhoWantsToBeAMillionaire?',
                'social_name': 'aov',
                'social_url': 'http://instagram.com/aov',
                'username': 'aov2',
                'website_url': 'https://artofvisuals.com'
            }

            client.post('/api/users', data=payload, format='multipart')

        auth_user = account_models.User.objects.get(username="aov2")
        target_user = account_models.User.objects.create_user(email='mrstest@artofvisuals.com', password='WhoAmI',
                                                              username='aov1')
        device = APNSDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=target_user)
        photo = photo_models.Photo(coordinates=Point(-116, 43),
                                   image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                                   user=target_user)
        photo.save()
        photo2 = photo_models.Photo(coordinates=Point(-116, 43),
                                    image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')),
                                    user=target_user)
        photo2.save()
        photo_models.Gallery.objects.create_or_update(
            name="Test Gallery", user=target_user, photos=photo_models.Photo.objects.all())

        message = "{} has upvoted your artwork.".format(auth_user.username)
        PushNotificationRecord.objects.create(message=message, receiver=device, action="U",
                                              content_object=photo, sender=auth_user)
        message = "{} has commented on your artwork.".format(auth_user.username)
        PushNotificationRecord.objects.create(message=message, receiver=device, action="C",
                                              content_object=photo, sender=auth_user)
        message = "Your artwork has been featured in the AOV Picks gallery!"
        PushNotificationRecord.objects.create(message=message, receiver=device, action="A",
                                              content_object=photo, sender=auth_user)
        message = "{} started following you.".format(auth_user.username)
        PushNotificationRecord.objects.create(message=message, receiver=device, action="F", content_object=target_user,
                                              sender=auth_user)

    def tearDown(self):
        """
            Clean out the data from each test for a clean slate

        :return: No return
        """

        account_models.User.objects.all().delete()
        photo_models.Photo.objects.all().delete()
        test_helpers.clear_directory('backend/media/', '*.jpg')

    def test_user_notification_record_view_set_get_successful(self):
        """
            Unit test to verify successful retrieval of a users notification history

        :return: No return
        """
        auth_user = account_models.User.objects.get(username="aov1")

        # Simulate auth
        token = test_helpers.get_token_for_user(auth_user)

        followed = PushNotificationRecord.objects.get(action="F")
        followed.created_at = timezone.now() - timedelta(days=8)
        followed.save()

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/notifications')
        results = request.data['results']

        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(results), 3)
