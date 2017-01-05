from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestGearSingleViewSetGET(TestCase):
    def test_gear_single_view_set_get_successful(self):
        """
        Test that we can get a gear entry

        :return: None
        """
        # Create test data
        gear = account_models.Gear.objects\
            .create_or_update(link='http://site.com/canon', item_make='Canon', item_model='EOS 5D Mark II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear/{}'.format(gear.id))
        result = request.data

        self.assertEquals(result['link'], gear.link)
        self.assertEquals(result['item_make'], gear.item_make)
        self.assertEquals(result['item_model'], gear.item_model)
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Query DB
        db_gear = account_models.Gear.objects.all()

        self.assertEquals(len(db_gear), 87)  # 86 created by fixture

        db_gear = db_gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertEquals(db_gear.id, gear.id)

    def test_gear_single_view_set_get_does_not_exist(self):
        """
        Test that we get 404 if no gear

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear/{}'.format(99999))

        self.assertEquals(request.status_code, 404)

    def test_gear_single_view_get_private(self):
        """
        Test that we get 404 if gear is private

        :return: None
        """
        # Create test data
        gear = account_models.Gear.objects \
            .create_or_update(link='http://site.com/canon', item_make='Canon', item_model='EOS 5D Mark II',
                              public=False)

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear/{}'.format(gear.id))

        self.assertEquals(request.status_code, 404)


class TestGearSingleViewSetPATCH(TestCase):
    """
    Test PATCH /api/gear/{}
    Only admins can edit
    """
    def test_gear_single_view_set_patch_successful(self):
        """
        Test that we can update gear

        :return: None
        """
        # Create test data
        gear = account_models.Gear.objects \
            .create_or_update(link='http://site.com/canon', item_make='Canon', item_model='EOS 5D Mark II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'http://amazon.com/canon',
            'item_make': 'Canon'
        }

        request = client.patch('/api/gear/{}'.format(gear.id), data=payload)
        result = request.data

        self.assertEquals(result['link'], 'http://amazon.com/canon')
        self.assertEquals(result['item_make'], gear.item_make)
        self.assertEquals(result['item_model'], gear.item_model)
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Query DB
        db_gear = account_models.Gear.objects.all()

        self.assertEquals(len(db_gear), 87)  # 86 created by fixture

        db_gear = db_gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertEquals(db_gear.id, gear.id)
        self.assertEquals(db_gear.link, 'http://amazon.com/canon')

    def test_gear_single_view_set_patch_not_found(self):
        """
        Test that we get 404 if gear not found

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'http://amazon.com/canon',
            'item_make': 'Canon'
        }

        request = client.patch('/api/gear/{}'.format(5555), data=payload)

        self.assertEquals(request.status_code, 404)

    def test_gear_single_view_set_patch_invalid(self):
        """
        Test that we get 400 if payload invalid

        :return: None
        """
        # Create test data
        gear = account_models.Gear.objects \
            .create_or_update(link='http://site.com/canon', item_make='Canon', item_model='EOS 5D Mark II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'http://amazon.com/canon',
            'item_make': 'Canon',
            'item_model': None
        }

        request = client.patch('/api/gear/{}'.format(gear.id), data=payload)

        self.assertEquals(request.status_code, 400)

        # Query DB
        db_gear = account_models.Gear.objects.all()

        self.assertEquals(len(db_gear), 87)  # 86 created by fixture

        db_gear = db_gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertEquals(db_gear.id, gear.id)
        self.assertEquals(db_gear.link, 'http://site.com/canon')
        self.assertTrue(db_gear.public)
        self.assertFalse(db_gear.reviewed)

    def test_gear_single_view_set_patch_not_admin(self):
        """
        Test that we get 403 if user is not admin

        :return: None
        """
        # Create test data
        gear = account_models.Gear.objects \
            .create_or_update(link='http://site.com/canon', item_make='Canon', item_model='EOS 5D Mark II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'http://amazon.com/canon',
            'item_make': 'Canon'
        }

        request = client.patch('/api/gear/{}'.format(gear.id), data=payload)

        self.assertEquals(request.status_code, 403)

        # Query DB
        db_gear = account_models.Gear.objects.all()

        self.assertEquals(len(db_gear), 87)  # 86 created by fixture

        db_gear = db_gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertEquals(db_gear.id, gear.id)
        self.assertEquals(db_gear.link, gear.link)
        self.assertEquals(db_gear.item_make, gear.item_make)
        self.assertEquals(db_gear.item_model, gear.item_model)
        self.assertTrue(db_gear.public)
        self.assertFalse(db_gear.reviewed)
