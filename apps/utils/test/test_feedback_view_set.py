from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.utils import models as utils_models
from django.core import mail
from django.test import TestCase
from fcm_django.models import FCMDevice
from rest_framework.test import APIClient
from unittest import mock


class TestFeedbackViewSetPOST(TestCase):
    """
    Test /api/utils/feedback
    """

    def setUp(self):
        """
            Sets up information for the test cases

        :return: None
        """
        user = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        FCMDevice.objects.create(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50',
                                 user=user, type="ios")

    def tearDown(self):
        """
            Deletes all entries in database to allow for a clean set up

        :return: None
        """
        account_models.User.objects.all().delete()
        FCMDevice.objects.all().delete()


    def test_feedback_view_set_post_bug_successful(self):
        """
        Test that we can create a feedback

        :return: None
        """
        # Retrieve the User
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        payload = {'feedback_type': 'bug', 'message': "This viewset is broken!"}

        request = client.post('/api/utils/feedback', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.Feedback.objects.all()

        self.assertEquals(len(actions), 1)
        self.assertEqual(actions.first().feedback_type, "B")
        self.assertEqual(len(mail.outbox), 1)

    def test_feedback_view_set_post_feature_request_successful(self):
        """
        Test that we can create a feedback

        :return: None
        """
        # Retrieve the User
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        payload = {'feedback_type': 'feature request', 'message': "You should add video support!"}

        request = client.post('/api/utils/feedback', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.Feedback.objects.all()

        self.assertEqual(actions.first().feedback_type, "F")
        self.assertEquals(len(actions), 1)

    def test_feedback_view_set_post_appreciation_successful(self):
        """
        Test that we can create a feedback

        :return: None
        """
        # Retrieve the User
        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        payload = {'feedback_type': 'appreciation', 'message': "AoV is what Instagram SHOULD be! Great app!"}

        request = client.post('/api/utils/feedback', data=payload, format='json')

        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.Feedback.objects.all()

        self.assertEquals(len(actions), 1)
        self.assertEqual(actions.first().feedback_type, "A")

    def test_feedback_view_set_post_reply_as_staff_successful(self):
        """
        Test that we can create a feedback

        :return: None
        """
        # Retrieve the User
        user = account_models.User.objects.get(username="aov_hov")


        # Create a feedback to reply to
        feedback = utils_models.Feedback.objects.create(feedback_type="F",
                                                        message="You should support video",
                                                        user=user)
        # Create the admin to make the reply
        admin = account_models.User.objects.create_user(email='admin@artofvisuals.com',
                                                        password='pass', username='aov_admin')

        # Create the FCM Device for Push Notification
        device = FCMDevice.objects.get(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=user, type="ios")

        admin.is_superuser = True
        admin.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(admin)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        payload = {'feedback_type': 'reply', 'reply': "This viewset is broken!"}

        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            request = client.post('/api/utils/feedback/{}/reply'.format(feedback.id), data=payload, format='json')
            p.assert_called_with(api_key=None, badge=None,
                                 data=None, icon=None,
                                 registration_ids=[device.registration_id], sound=None,
                                 title=None,
                                 body="AoV has responded to your feedback. Check your associated email inbox!".format(
                                     user.username),)


        self.assertEquals(request.status_code, 200)

        # Check for entry
        actions = utils_models.Feedback.objects.all()

        self.assertEquals(len(actions), 1)
        self.assertEqual(actions.first().feedback_type, "F")
        self.assertTrue(actions.first().has_reply)
        self.assertIsNotNone(actions.first().reply_timestamp)
        self.assertEqual(len(mail.outbox), 1)

    def test_feedback_view_set_post_reply_fails(self):
        """
        Test that we can create a feedback

        :return: None
        """
        # Retrieve the User
        user = account_models.User.objects.get(username="aov_hov")


        # Create a feedback to reply to
        feedback = utils_models.Feedback.objects.create(feedback_type="F",
                                                        message="You should support video",
                                                        user=user)
        # Create the admin to make the reply
        non_admin = account_models.User.objects.create_user(email='admin@artofvisuals.com',
                                                            password='pass', username='aov_admin')

        # Simulate auth
        token = test_helpers.get_token_for_user(non_admin)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        payload = {'feedback_type': 'reply', 'reply': "This viewset is broken!"}

        request = client.post('/api/utils/feedback/{}/reply'.format(feedback.id), data=payload, format='json')

        self.assertEquals(request.status_code, 400)

        # Check for entry
        actions = utils_models.Feedback.objects.all()

        self.assertEquals(len(actions), 1)
        self.assertEqual(actions.first().feedback_type, "F")
        self.assertFalse(actions.first().has_reply)
        self.assertIsNone(actions.first().reply_timestamp)
