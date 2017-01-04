from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestGearViewSetGET(TestCase):
    """
    GET /api/gear
    """
    def test_gear_view_set_get_successful(self):
        """
        Test that we can get gear

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(link='http://site.com/canon', make='Canon', model='EOS 5D Mark II')
        account_models.Gear.objects.create_or_update(make='Sony', model='a99 II', reviewed=True)

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 2)

        self.assertIsNotNone(results[0]['link'])
        self.assertEquals(results[0]['make'], 'Canon')
        self.assertEquals(results[0]['model'], 'EOS 5D Mark II')
        self.assertFalse(results[0]['reviewed'])

        self.assertIsNone(results[1]['link'])
        self.assertEquals(results[1]['make'], 'Sony')
        self.assertTrue(results[1]['reviewed'])

    def test_gear_view_set_get_public(self):
        """
        Test that we can get only public gear

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(make='Canon', model='EOS 5D Mark II')
        account_models.Gear.objects.create_or_update(make='Sony', model='a99 II')
        account_models.Gear.objects.create_or_update(make='Sony', model='A7', public=False)

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 2)

        # Check for entries
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 3)


class TestGearViewSetPOST(TestCase):
    """
    POST /api/gear
    """
    def test_gear_view_set_post_successful(self):
        """
        Test that any user can create gear

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertEquals(result['make'], 'Canon')
        self.assertEquals(result['model'], 'EOS 5D Mark II')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)

        gear = gear.first()

        self.assertIsNone(gear.link)
        self.assertEquals(gear.make, 'Canon')
        self.assertEquals(gear.model, 'EOS 5D Mark II')
        self.assertTrue(gear.public)
        self.assertFalse(gear.reviewed)

    def test_gear_view_set_post_admin_successful(self):
        """
        Test that admin can create gear

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertEquals(result['make'], 'Canon')
        self.assertEquals(result['model'], 'EOS 5D Mark II')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)

        gear = gear.first()

        self.assertIsNone(gear.link)
        self.assertEquals(gear.make, 'Canon')
        self.assertEquals(gear.model, 'EOS 5D Mark II')
        self.assertTrue(gear.public)
        self.assertFalse(gear.reviewed)

    def test_gear_view_set_post_dupe(self):
        """
        Test that we get 409 if make + model already exists

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(link='http://site.com/canon', make='Canon', model='EOS 5D Mark II')
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II',
            'reviewed': True
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 409)

        # Check DB
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)
        self.assertFalse(gear[0].reviewed)

    def test_gear_view_set_post_invalid(self):
        """
        Test that we can get 400 is payload is invalid

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 400)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 0)

    def test_gear_view_set_post_link_successful(self):
        """
        Test that admin can add link

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'https://test.com/canon',
            'make': 'Canon',
            'model': 'EOS 5D Mark II'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNotNone(result['link'])
        self.assertEquals(result['make'], 'Canon')
        self.assertEquals(result['model'], 'EOS 5D Mark II')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)

        gear = gear.first()

        self.assertIsNotNone(gear.link)
        self.assertEquals(gear.make, 'Canon')
        self.assertEquals(gear.model, 'EOS 5D Mark II')
        self.assertTrue(gear.public)
        self.assertFalse(gear.reviewed)

    def test_gear_view_set_post_link_not_admin(self):
        """
        Test that non-admin cannot add link

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'link': 'https://test.com/canon',
            'make': 'Canon',
            'model': 'EOS 5D Mark II'
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 403)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 0)

    def test_gear_view_set_post_private(self):
        """
        Test that we can create non-public gear

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II',
            'public': False
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNone(result['link'])
        self.assertEquals(result['make'], 'Canon')
        self.assertEquals(result['model'], 'EOS 5D Mark II')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)

        gear = gear.first()

        self.assertIsNone(gear.link)
        self.assertEquals(gear.make, 'Canon')
        self.assertEquals(gear.model, 'EOS 5D Mark II')
        self.assertFalse(gear.public)
        self.assertFalse(gear.reviewed)

        # Now get all gear and expect none
        gear_request = client.get('/api/gear')

        self.assertEquals(len(gear_request.data['results']), 0)

    def test_gear_view_set_post_reviewed_successful(self):
        """
        Test that admin can mark gear as reviewed

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II',
            'reviewed': True
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNone(result['link'])
        self.assertEquals(result['make'], 'Canon')
        self.assertEquals(result['model'], 'EOS 5D Mark II')
        self.assertNotIn('public', result)
        self.assertTrue(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 1)

        gear = gear.first()

        self.assertIsNone(gear.link)
        self.assertEquals(gear.make, 'Canon')
        self.assertEquals(gear.model, 'EOS 5D Mark II')
        self.assertTrue(gear.public)
        self.assertTrue(gear.reviewed)

    def test_gear_view_set_post_reviewed_not_admin(self):
        """
        Test that non-admin cannot mark gear as reviewed

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'make': 'Canon',
            'model': 'EOS 5D Mark II',
            'reviewed': True
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 403)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 0)
