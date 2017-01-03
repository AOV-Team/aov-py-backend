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
