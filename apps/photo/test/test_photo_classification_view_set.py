from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from django.test import TestCase
from rest_framework.test import APIClient


class TestPhotoClassificationViewSetGET(TestCase):
    """
    Test /api/photo_classifications
    """
    def test_photo_classification_view_set_get_successful(self):
        """
        Test that we can successfully get all classifications

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoClassification.objects.create_or_update(name='City')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')
        photo_models.PhotoClassification.objects.create_or_update(name='Rural', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications')
        results = request.data['results']

        # 11 classifications are created by fixture
        self.assertEquals(len(results), 14)
        self.assertEquals(results[2]['classification_type'], 'category')

    def test_photo_classification_view_set_get_filtered_successful(self):
        """
        Test that we can successfully get all classifications for one type ("tag")

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoClassification.objects.create_or_update(name='City')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')
        photo_models.PhotoClassification.objects.create_or_update(name='Urban', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications?classification=tag')
        results = request.data['results']

        self.assertEquals(len(results), 2)

    def test_photo_classification_view_set_get_filtered_does_not_exist(self):
        """
        Test that we get 400 if classification type does not exist

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoClassification.objects.create_or_update(name='City')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')
        photo_models.PhotoClassification.objects.create_or_update(name='Urban', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications?classification=group')

        self.assertEquals(request.status_code, 400)

    def test_photo_classification_view_set_get_not_authenticated(self):
        """
        Test that we can successfully get all classifications even if not authenticated

        :return: None
        """
        # Test data
        photo_models.PhotoClassification.objects.create_or_update(name='City')
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')
        photo_models.PhotoClassification.objects.create_or_update(name='Rural', classification_type='category')

        # Get data from endpoint
        client = APIClient()

        request = client.get('/api/photo_classifications')
        results = request.data['results']

        # 11 classifications are created by fixture
        self.assertEquals(len(results), 14)
        self.assertEquals(results[2]['classification_type'], 'category')

    def test_photo_classification_view_set_get_public(self):
        """
        Test that we can successfully get all public classifications

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI', username='aov1')

        photo_models.PhotoClassification.objects.create_or_update(name='City', public=False)
        photo_models.PhotoClassification.objects.create_or_update(name='Abstract')
        photo_models.PhotoClassification.objects.create_or_update(name='Rural', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        request = client.get('/api/photo_classifications')
        results = request.data['results']

        self.assertEquals(len(results), 13)


class TestPhotoClassificationViewSetPOST(TestCase):
    """
    Test POST /api/photo_classifications
    """
    def test_photo_classification_view_set_post_successful(self):
        """
        Test that we can create a tag

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
            'name': 'Night',
            'classification_type': 'tag'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')
        result = request.data

        self.assertEquals(result['name'], 'Night')

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        # 11 classifications are loaded by fixture
        self.assertEquals(len(classifications), 12)

    def test_photo_classification_view_set_post_category_not_allowed(self):
        """
        Test that we cannot create a new category

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI',
                                                       username='aov1')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'name': 'Night',
            'classification_type': 'category'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 11)

    def test_photo_classification_view_set_post_category_update_not_allowed(self):
        """
        Test that we cannot update existing category

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI',
                                                       username='aov1')
        photo_models.PhotoClassification.objects.create_or_update(name='night', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'name': 'Night',
            'classification_type': 'category'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 12)

    def test_photo_classification_view_set_post_tag_category_exists(self):
        """
        Test that we create new tag even if category already exists

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI',
                                                       username='aov1')
        photo_models.PhotoClassification.objects.create_or_update(name='night', classification_type='category')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'name': 'Night',
            'classification_type': 'tag'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')
        result = request.data

        self.assertEquals(result['name'], 'Night')
        self.assertEquals(result['classification_type'], 'tag')

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 13)

    def test_photo_classification_view_set_post_category_not_authenticated(self):
        """
        Test that unauthenticated users cannot create a tag

        :return: None
        """
        # Get data from endpoint
        client = APIClient()

        payload = {
            'name': 'Night',
            'classification_type': 'tag'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')
        self.assertEquals(request.status_code, 401)

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 11)

    def test_photo_classification_view_set_post_not_public(self):
        """
        Test that we cannot create private tag

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
            'name': 'Night',
            'classification_type': 'tag',
            'public': False
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 11)

    def test_photo_classification_view_set_post_update(self):
        """
        Test that tag updates if it already exists

        :return: None
        """
        # Test data
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='WhoAmI',
                                                       username='aov1')
        photo_models.PhotoClassification.objects.create_or_update(name='night', classification_type='tag')

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        payload = {
            'name': 'Night',
            'classification_type': 'tag'
        }

        request = client.post('/api/photo_classifications', data=payload, format='json')
        result = request.data

        self.assertEquals(result['name'], 'Night')

        # Query for entry as well
        classifications = photo_models.PhotoClassification.objects.all()

        self.assertEquals(len(classifications), 12)
        self.assertEquals(classifications[11].name, 'Night')
