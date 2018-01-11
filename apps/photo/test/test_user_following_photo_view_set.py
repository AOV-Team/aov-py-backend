from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APIClient


class TestUserFollowingPhotoViewSetGET(TestCase):
    """
    Test GET api/me/following/photos

    :author: gallen
    """
    def test_user_following_photo_view_set_get_successful(self):
        """
        Test that we can get photos

        :return: None
        """
        # Test data
        target_user = account_models.User.objects.create_user(age=25, email='mrtest1@mypapaya.io',
                                                              social_name='@ronquilloaeon', username='aov_hov')
        user_1 = account_models.User.objects.create_user(email='travis@aov.com', social_name='@travis', username='aov')
        user_2 = account_models.User.objects.create_user(email='prince@aov.com', social_name='@wbp', username='wbp')

        access_user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        access_user.location = 'Boise'
        access_user.social_name = '@theaov'
        access_user.save()

        # Follow target user
        target_user.follower.add(access_user)
        target_user.save()
        user_1.follower.add(access_user)
        user_1.save()
        user_2.follower.add(access_user)
        user_2.save()

        category = photo_models.PhotoClassification.objects.create_or_update(name='Night',
                                                                             classification_type='category')

        # Create some gear
        gear_1 = account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II')
        gear_2 = account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II')

        photo1 = photo_models \
            .Photo(coordinates=Point(-116, 43), image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')),
                   user=user_2)
        photo1.save()
        photo1.gear.add(gear_1, gear_2)
        photo1.category.add(category)
        photo1.votes = 1
        photo1.photo_feed.add(1)
        photo1.save()

        photo2 = photo_models \
            .Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user_1)
        photo2.save()
        photo2.votes = 12
        photo2.category.add(category)
        photo2.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(access_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/me/following/photos', format='json')
        data = request.data

        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["user_details"]["id"], user_1.id)

    def test_user_following_photo_view_set_get_not_logged_in(self):
        """
            Unit test to verify 401 on request without authentication

        :return: No return
        """

        # Get data from endpoint
        client = APIClient()

        request = client.get('/api/me/following/photos', format='json')

        self.assertEqual(request.status_code, 403)
