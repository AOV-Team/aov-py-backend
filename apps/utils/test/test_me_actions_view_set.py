from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from apps.utils import models as utils_models
from django.test import TestCase
from rest_framework.test import APIClient


class TestMeActionsViewSetPOST(TestCase):
    """
    Test /api/me/actions
    """
    def test_me_actions_view_set_post_successful(self):
        """
        Test that we can create an action

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        category = photo_models.PhotoClassification.objects\
            .create_or_update(name='Misc', classification_type='category')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo.category = [category]
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/actions', data={'action': 'photo_click', 'id': photo.id}, format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.UserAction.objects.all()

        self.assertEquals(len(actions), 1)
        self.assertEquals(actions[0].action, 'photo_click')

    def test_me_actions_view_set_post_twice(self):
        """
        Test that we can create two distinct actions

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Misc', classification_type='category')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo.category = [category]
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Two actions, same type and user
        request = client.post('/api/me/actions', data={'action': 'photo_click', 'id': photo.id}, format='json')

        self.assertEquals(request.status_code, 200)

        request = client.post('/api/me/actions', data={'action': 'photo_click', 'id': photo.id}, format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.UserAction.objects.all()

        self.assertEquals(len(actions), 2)
        self.assertEquals(actions[0].action, 'photo_click')

        distinct_actions = utils_models.UserAction.objects.all().distinct('user__id')

        self.assertEquals(len(distinct_actions), 1)

    def test_me_actions_view_set_post_bad_action(self):
        """
        Test that we get 400 if action is not valid

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        category = photo_models.PhotoClassification.objects \
            .create_or_update(name='Misc', classification_type='category')

        photo = photo_models.Photo(image=Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb')), user=user)
        photo.save()
        photo.category = [category]
        photo.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/actions', data={'action': 'photo_c', 'id': photo.id}, format='json')

        self.assertEquals(request.status_code, 400)

        # Check for entry
        actions = utils_models.UserAction.objects.all()

        self.assertEquals(len(actions), 0)

    def test_me_actions_view_set_post_bad_request(self):
        """
        Test that we get 400 if missing a key

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/actions', data={'id': 55555}, format='json')

        self.assertEquals(request.status_code, 400)

        # Check for entry
        actions = utils_models.UserAction.objects.all()

        self.assertEquals(len(actions), 0)

    def test_me_actions_view_set_post_photo_does_not_exist(self):
        """
        Test that we get 404 if photo does not exist (photo action)

        :return: None
        """
        # Create test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.post('/api/me/actions', data={'action': 'photo_click', 'id': 55555}, format='json')

        self.assertEquals(request.status_code, 404)

        # Check for entry
        actions = utils_models.UserAction.objects.all()

        self.assertEquals(len(actions), 0)
