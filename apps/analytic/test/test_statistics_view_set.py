from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo import signals as photo_signals
from apps.photo.photo import Photo
from django.test import override_settings, TestCase
from freezegun import freeze_time
from rest_framework.test import APIClient
from datetime import datetime


@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestStatisticsViewSetGET(TestCase):
    def setUp(self):
        # Disconnect cache generation, otherwise boto causes unit tests to fail due to testing w/ non-present dates
        photo_signals.post_save.disconnect(photo_signals.save_photo_image_caches, sender=photo_models.Photo)

    def tearDown(self):
        # Reconnect cache generation so other unit tests don't fail
        photo_signals.post_save.connect(photo_signals.save_photo_image_caches, sender=photo_models.Photo)

        test_helpers.clear_directory('backend/media/', '*.jpg')
        test_helpers.clear_directory('backend/media/', '20*_apps')

    @freeze_time('2017-03-21', tz_offset=-7)
    def test_statistics_view_set_photo_get_successful(self):
        """
        Test that we can get photo stats

        :return: None
        """
        # Create test users
        user = account_models.User.objects.create_superuser('admin@aov.com', 'pass')
        user.is_admin = True
        user.created_at = datetime(year=2016, month=12, day=31)
        user.save()

        user_1 = account_models.User.objects.create_user('test1@aov.com', 'test1', 'pass')
        user_1.created_at = datetime(year=2017, month=1, day=12)
        user_1.save()

        user_2 = account_models.User.objects.create_user('test2@aov.com', 'test2', 'pass')
        user_2.created_at = datetime(year=2017, month=1, day=15)
        user_2.save()

        user_3 = account_models.User.objects.create_user('test3@aov.com', 'test3', 'pass')
        user_3.created_at = datetime(year=2017, month=1, day=29)
        user_3.save()

        user_4 = account_models.User.objects.create_user('test4@aov.com', 'test4', 'pass')
        user_4.created_at = datetime(year=2017, month=1, day=31, hour=23, minute=59, second=59)
        user_4.save()

        user_5 = account_models.User.objects.create_user('test5@aov.com', 'test5', 'pass')
        user_5.created_at = datetime(year=2017, month=2, day=17)
        user_5.save()

        user_6 = account_models.User.objects.create_user('test6@aov.com', 'test6', 'pass')
        user_6.created_at = datetime(year=2017, month=2, day=21)
        user_6.save()

        user_7 = account_models.User.objects.create_user('test7@aov.com', 'test7', 'pass')
        user_7.created_at = datetime(year=2017, month=3, day=1, hour=0, minute=0, second=0)
        user_7.save()

        # Create test photos
        category_1 = photo_models.PhotoClassification.objects.get(name='Other')
        category_2 = photo_models.PhotoClassification.objects.get(name='Urban')

        photo_1 = photo_models.Photo.objects.create(image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_1.category = [category_1]
        photo_1.created_at = datetime(year=2017, month=1, day=10)
        photo_1.save()

        photo_2 = photo_models.Photo.objects.create(
            user=user_1, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_2.category = [category_1]
        photo_2.created_at = datetime(year=2017, month=1, day=12)
        photo_2.save()

        photo_3 = photo_models.Photo.objects.create(
            user=user_2, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_3.category = [category_2]
        photo_3.created_at = datetime(year=2017, month=1, day=16)
        photo_3.save()

        photo_4 = photo_models.Photo.objects.create(
            user=user_3, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_4.category = [category_1]
        photo_4.created_at = datetime(year=2017, month=1, day=31)
        photo_4.save()

        photo_5 = photo_models.Photo.objects.create(
            user=user_4, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_5.category = [category_1]
        photo_5.created_at = datetime(year=2017, month=2, day=2)
        photo_5.save()

        photo_6 = photo_models.Photo.objects.create(
            user=user_5, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_6.category = [category_1]
        photo_6.created_at = datetime(year=2017, month=2, day=18)
        photo_6.save()

        photo_7 = photo_models.Photo.objects.create(
            user=user_6, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_7.category = [category_1]
        photo_7.created_at = datetime(year=2017, month=2, day=23)
        photo_7.save()

        photo_8 = photo_models.Photo.objects.create(
            user=user_7, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_8.category = [category_2]
        photo_8.created_at = datetime(year=2017, month=3, day=1)
        photo_8.save()

        photo_9 = photo_models.Photo.objects.create(
            user=user_7, image=Photo(open('apps/common/test/data/photos/small.jpg', 'rb')))
        photo_9.category = [category_2]
        photo_9.created_at = datetime(year=2017, month=3, day=2)
        photo_9.save()

        client = APIClient()
        client.force_authenticate(user)

        request = client.get('/api/statistics/photos')
        results = request.data['results']

        self.assertEquals(len(results), 4)  # 3 months of data
        self.assertEquals(results[0]['date'], '2016-12-1')
        self.assertEquals(results[0]['average_photos_per_user'], 0)
        self.assertEquals(results[1]['date'], '2017-1-1')
        self.assertEquals(results[1]['average_photos_per_user'], 0.80)
        self.assertEquals(results[2]['date'], '2017-2-1')
        self.assertEquals(results[2]['average_photos_per_user'], 1.0)
        self.assertEquals(results[3]['date'], '2017-3-1')
        self.assertEquals(results[3]['average_photos_per_user'], 1.12)
