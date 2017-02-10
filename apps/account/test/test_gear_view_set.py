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
        account_models.Gear.objects.create_or_update(link='http://site.com/canon', item_make='Canon',
                                                     item_model='EOS 5D Mark II Test')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II Test', reviewed=True)

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 88)  # 86 are created by fixture

        counter = 0  # Keep track that we have checked our items

        for r in results:
            if r['item_make'] == 'Canon' and r['item_model'] == 'EOS 5D Mark II Test':
                self.assertIsNotNone(r['link'])
                self.assertFalse(r['reviewed'])
                counter += 1

            if r['item_make'] == 'Sony' and r['item_model'] == 'a99 II Test':
                self.assertIsNone(r['link'])
                self.assertTrue(r['reviewed'])
                counter += 1

        self.assertEquals(counter, 2)

    def test_gear_view_set_get_public(self):
        """
        Test that we can get only public gear

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II Test')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II Test')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='A7 Test', public=False)

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 88)  # 86 are created by fixture

        # Check for entries
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 89)

    def test_gear_view_set_get_search_make(self):
        """
        Test that we can search gear by make

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II Test')
        account_models.Gear.objects.create_or_update(item_make='Random Brand', item_model='a99 II Test')
        account_models.Gear.objects.create_or_update(item_make='Random Brand', item_model='A7 Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear?item_make=ran')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 2)

    def test_gear_view_set_get_search_make_model(self):
        """
        Test that we can search gear by make and model

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(item_make='Units', item_model='eZee 500')
        account_models.Gear.objects.create_or_update(item_make='Units', item_model='ezee 700a II Test')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear?item_make=unit&item_model=ezee')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]['item_model'], 'eZee 500')

    def test_gear_view_set_get_search_model(self):
        """
        Test that we can search gear by make

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Test Model')
        account_models.Gear.objects.create_or_update(item_make='Canon', item_model='EOS 5D Mark II Test Model')
        account_models.Gear.objects.create_or_update(item_make='Sony', item_model='a99 II Test')

        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/gear?item_model=model')
        results = request.data['results']

        self.assertIsNone(request.data['next'])
        self.assertEquals(len(results), 2)


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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertEquals(result['item_make'], 'Canon')
        self.assertEquals(result['item_model'], 'EOS 5D Mark II Test')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 87)  # 86 are created by fixture

        gear = gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertIsNone(gear.link)
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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertEquals(result['item_make'], 'Canon')
        self.assertEquals(result['item_model'], 'EOS 5D Mark II Test')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 87)  # 86 are created by fixture

        gear = gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertIsNone(gear.link)
        self.assertEquals(gear.item_make, 'Canon')
        self.assertEquals(gear.item_model, 'EOS 5D Mark II Test')
        self.assertTrue(gear.public)
        self.assertFalse(gear.reviewed)

    def test_gear_view_set_post_dupe(self):
        """
        Test that we get 409 if make + model already exists

        :return: None
        """
        # Create test data
        account_models.Gear.objects.create_or_update(link='http://site.com/canon', item_make='Canon',
                                                     item_model='EOS 5D Mark II')
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')
        user.is_admin = True
        user.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II',
            'reviewed': False
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 409)

        # Check DB
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 86)  # 86 are created by fixture
        self.assertTrue(gear[0].reviewed)

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
            'item_make': 'Canon',
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 400)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 86)  # 86 are created by fixture

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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test'
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNotNone(result['link'])
        self.assertEquals(result['item_make'], 'Canon')
        self.assertEquals(result['item_model'], 'EOS 5D Mark II Test')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 87)  # 86 are created by fixture

        gear = gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertIsNotNone(gear.link)
        self.assertEquals(gear.item_make, 'Canon')
        self.assertEquals(gear.item_model, 'EOS 5D Mark II Test')
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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test'
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 403)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 86)  # 86 are created by fixture

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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test',
            'public': False
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNone(result['link'])
        self.assertEquals(result['item_make'], 'Canon')
        self.assertEquals(result['item_model'], 'EOS 5D Mark II Test')
        self.assertNotIn('public', result)
        self.assertFalse(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 87)  # 86 are created by fixture

        gear = gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertIsNone(gear.link)
        self.assertEquals(gear.item_make, 'Canon')
        self.assertEquals(gear.item_model, 'EOS 5D Mark II Test')
        self.assertFalse(gear.public)
        self.assertFalse(gear.reviewed)

        # Now get all gear and expect 86
        gear_request = client.get('/api/gear')

        self.assertEquals(len(gear_request.data['results']), 86)

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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test',
            'reviewed': True
        }

        request = client.post('/api/gear', data=payload)
        result = request.data

        self.assertIsNone(result['link'])
        self.assertEquals(result['item_make'], 'Canon')
        self.assertEquals(result['item_model'], 'EOS 5D Mark II Test')
        self.assertNotIn('public', result)
        self.assertTrue(result['reviewed'])

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 87)  # 86 are created by fixture

        gear = gear.get(item_make='Canon', item_model='EOS 5D Mark II Test')

        self.assertIsNone(gear.link)
        self.assertEquals(gear.item_make, 'Canon')
        self.assertEquals(gear.item_model, 'EOS 5D Mark II Test')
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
            'item_make': 'Canon',
            'item_model': 'EOS 5D Mark II Test',
            'reviewed': True
        }

        request = client.post('/api/gear', data=payload)

        self.assertEquals(request.status_code, 403)

        # Check DB entry
        gear = account_models.Gear.objects.all()

        self.assertEquals(len(gear), 86)  # 86 are created by fixture
