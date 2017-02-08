from apps.account.models import User
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from apps.utils.models import UserAction
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoSingleFlagsViewSetPOST(TestCase):
    def test_photo_single_flags_view_set_post_successful(self):
        """
        Test that we can successfully flag a photo

        :return: None
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        request = client.post('/api/photos/{}/flags'.format(photo.id))

        self.assertEquals(request.status_code, 201)

        # Check db
        actions = UserAction.objects.all()

        self.assertEquals(actions.count(), 1)

        action = actions.first()

        self.assertEquals(action.user, user)
        self.assertEquals(action.action, 'photo_flag')

    def test_photo_single_flags_view_set_post_already_flagged(self):
        """
        Test that nothing changes if user has already flagged a photo (except for 200 response code)

        :return: None
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo2-min.jpg', 'rb')), user=user)
        photo.save()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        request = client.post('/api/photos/{}/flags'.format(photo.id))

        self.assertEquals(request.status_code, 201)

        # Do it again!
        request = client.post('/api/photos/{}/flags'.format(photo.id))

        self.assertEquals(request.status_code, 200)  # Expect 200 if flag already existed

        # Check db
        actions = UserAction.objects.all()

        self.assertEquals(actions.count(), 1)

        action = actions.first()

        self.assertEquals(action.user, user)
        self.assertEquals(action.action, 'photo_flag')

    def test_photo_single_flags_view_set_post_photo_does_not_exist(self):
        """
        Test that we get 404 if photo does not exist

        :return: None
        """
        user = User.objects.create_user('test@aov.com', 'testuser', 'pass')

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + test_helpers.get_token_for_user(user))

        request = client.post('/api/photos/{}/flags'.format(9999999))

        self.assertEquals(request.status_code, 404)

        # Check db
        actions = UserAction.objects.all()

        self.assertEquals(actions.count(), 0)
