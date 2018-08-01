from apps.account import models as account_models
from apps.communication.models import PushNotificationRecord
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice
from unittest import mock
import time

@override_settings(REMOTE_IMAGE_STORAGE=False,
                   DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestPhotoSave(TestCase):
    """
    Test GET api/photos
    """
    def test_photo_save_successful(self):
        """
        Test that when saving a photo with the AoV Picks feed, it sets the date correctly

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create_or_update(name="AOV Picks"))
        photo1.save()

        updated_photo = photo_models.Photo.objects.get(id=photo1.id)
        self.assertEqual(len(updated_photo.photo_feed.all()), 1)
        self.assertIsNotNone(updated_photo.aov_feed_add_date)

    def test_photo_save_aov_date_unchanged_upon_future_save(self):
        """
            Unit test to validate that aov_feed_add_date doesn't change once set.

        :return: No return
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        # Create the photo
        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create_or_update(name="AOV Picks"))
        photo1.save()
        original_add_date = photo_models.Photo.objects.get(id=photo1.id).aov_feed_add_date
        time.sleep(2)
        photo1.save()

        updated_photo = photo_models.Photo.objects.get(id=photo1.id)
        self.assertEqual(len(updated_photo.photo_feed.all()), 1)
        self.assertTrue(updated_photo.aov_feed_add_date == original_add_date)

    def test_photo_save_sends_notification_when_added_to_picks(self):
        """
            Unit test to validate that a push notification is sent when the image is added to the AoV Picks.

        :return:
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')
        device = FCMDevice.objects \
            .create( registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50',
                     user=user, type="ios")

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create_or_update(name="AOV Picks"))
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            photo1.save()


            p.assert_called_with(
                api_key=None, badge=None,
                data=None, icon=None,
                registration_ids=[device.registration_id], sound=None,
                title=None,
                body="Your artwork has been featured in the AOV Picks gallery, {}!".format(user.username),
                )

        updated_photo = photo_models.Photo.objects.get(id=photo1.id)
        self.assertEqual(len(updated_photo.photo_feed.all()), 1)
        self.assertIsNotNone(updated_photo.aov_feed_add_date)
        self.assertEqual(PushNotificationRecord.objects.count(), 1)
        self.assertIsNotNone(PushNotificationRecord.objects.first().fcm_receiver)
        self.assertIsNone(PushNotificationRecord.objects.first().receiver)

    def test_photo_save_sends_notification_only_once_when_added_to_picks(self):
        """
            Unit test to verify that subsequent calls to .save() for a photo do not send the AoV Picks push notification
            every time after the initial adding

        :return: No return
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')
        device = FCMDevice.objects \
            .create(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50',
                    user=user, type="ios")

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create_or_update(name="AOV Picks"))
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            photo1.save()

            p.assert_called_with(api_key=None, badge=None,
                data=None, icon=None,
                registration_ids=[device.registration_id], sound=None,
                title=None,
                body="Your artwork has been featured in the AOV Picks gallery, {}!".format(user.username),)

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            photo1.save()

            p.assert_not_called()

        updated_photo = photo_models.Photo.objects.get(id=photo1.id)
        self.assertEqual(len(updated_photo.photo_feed.all()), 1)
        self.assertIsNotNone(updated_photo.aov_feed_add_date)
        self.assertEqual(PushNotificationRecord.objects.count(), 1)
        self.assertIsNotNone(PushNotificationRecord.objects.first().fcm_receiver)
        self.assertIsNone(PushNotificationRecord.objects.first().receiver)

    def test_photo_save_successful_no_fcm_device(self):
        """
            Unit test to verify the photo still saves successfully, even if a notification is not sent

        :return: No return value
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.location = 'Boise'
        user.social_name = '@theaov'
        user.save()
        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(photo_models.PhotoFeed.objects.create_or_update(name="AOV Picks"))
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            photo1.save()

            p.assert_not_called()

        updated_photo = photo_models.Photo.objects.get(id=photo1.id)
        self.assertEqual(len(updated_photo.photo_feed.all()), 1)
        self.assertIsNotNone(updated_photo.aov_feed_add_date)
        self.assertEqual(PushNotificationRecord.objects.count(), 0)

