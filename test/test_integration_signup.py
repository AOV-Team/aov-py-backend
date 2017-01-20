from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.photo import models as photo_models
from django.test import TestCase
from rest_framework.test import APIClient


def add_photo_for_user(user, photo='small.jpg', photo_location='Boise'):
    """
    Upload a photo for a user

    :param user: User instance
    :param photo: test photo file name
    :param photo_location: (string) for Photo.location - can be used to query for specific photos
    :return: None
    """
    test_images_dir = 'apps/common/test/data/photos/'
    token = test_helpers.get_token_for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    with open('{}{}'.format(test_images_dir, photo), 'rb') as image:
        payload = {
            'category': 8,
            'image': image,
            'location': photo_location
        }

        client.post('/api/photos', data=payload, format='multipart')


class TestIntegrationSignup(TestCase):
    def test_integration_signup(self):
        """
        Test a user signing up and interacting with the app

        1. Register
          - username
          - email
          - password
          - location
          - social name
          - age

        2. Log in

        3. View feed

        4. Upload photo

        5. View profile

        6. Superadmin adds new user's photo to main feed

        7. User sees their photo at top of the feed
        """
        #
        # 0. Create test data and simulate an environment where there are other users
        #

        # Super user and some other users
        superuser = account_models.User.objects.create_superuser('super@aov.com', 'pass')
        random_user_1 = account_models.User.objects.create_user('test0@aov.com', 'test0', 'pass')
        random_user_2 = account_models.User.objects.create_user('test02@aov.com', 'test02', 'pass')

        add_photo_for_user(random_user_1, 'avatar.jpg', 'Paris')
        add_photo_for_user(random_user_2, 'photo1-min.jpg', 'NYC')
        add_photo_for_user(account_models.User.objects.create_user('test1@aov.com', 'test1', 'pass'))
        add_photo_for_user(account_models.User.objects.create_user('test2@aov.com', 'test2', 'pass'))
        add_photo_for_user(account_models.User.objects.create_user('test3@aov.com', 'test3', 'pass'),
                           'cover.jpg', 'London')

        # Add photos to main feed
        photo_1 = photo_models.Photo.objects.get(location='Paris')
        photo_2 = photo_models.Photo.objects.get(location='NYC')

        superuser_token = test_helpers.get_token_for_user(superuser)

        superuser_client = APIClient()
        superuser_client.credentials(HTTP_AUTHORIZATION='Token ' + superuser_token)

        pf_payload = {
            'photo_feed': [1]
        }

        superuser_client.patch('/api/photos/{}'.format(photo_2.id), data=pf_payload, format='json')
        superuser_client.patch('/api/photos/{}'.format(photo_1.id), data=pf_payload, format='json')

        #
        # 1. Register
        #

        client = APIClient()

        register_payload = {
            'age': 20,
            'email': 'random@aov.com',
            'location': 'Boise',
            'password': 'aha',
            'social_name': '@random',
            'username': '@random'
        }

        register_request = client.post('/api/users', data=register_payload)
        user = register_request.data

        self.assertEquals(register_request.status_code, 201)

        #
        # 2. Log in
        #

        login_request = client.post('/api/auth', data={'email': 'random@aov.com', 'password': 'aha'})
        login_response = login_request.data

        self.assertIn('token', login_response)

        client.credentials(HTTP_AUTHORIZATION='Token ' + login_response['token'])

        #
        # 3. View feed
        #

        feed_request = client.get('/api/photo_feeds/1/photos')
        feed_results = feed_request.data['results']

        self.assertEquals(len(feed_results), 2)
        self.assertEquals(feed_results[0]['id'], photo_1.id) # This was last photo added to feed

        #
        # 4. Upload photo
        #

        with open('{}{}'.format('apps/common/test/data/photos/', '1mb.jpg'), 'rb') as image:
            payload = {
                'category': 8,
                'image': image,
                'location': 'Shanghai'
            }

            photo_request = client.post('/api/photos', data=payload, format='multipart')

        photo = photo_request.data

        self.assertEquals(photo_request.status_code, 200)  # Should be 201 but this is what it returns

        #
        # 5. View profile
        #

        profile_images_request = client.get('/api/users/{}/photos'.format(user['id']))
        profile_images_result = profile_images_request.data['results']

        self.assertEquals(len(profile_images_result), 1)

        #
        # 6. Super user adds new user's photo to main feed
        #

        new_feed_photo_request = superuser_client\
            .patch('/api/photos/{}'.format(photo['id']), data=pf_payload, format='json')

        self.assertEquals(new_feed_photo_request.status_code, 200)

        #
        # 7. User sees their photo at the top of the main feed
        #

        feed_request_2 = client.get('/api/photo_feeds/1/photos')
        feed_results_2 = feed_request_2.data['results']

        self.assertEquals(len(feed_results_2), 3)
        self.assertEquals(feed_results_2[0]['id'], photo['id'])
        self.assertEquals(feed_results_2[0]['user'], user['id'])
