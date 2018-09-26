from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import DirectMessage, PushNotificationRecord, Conversation
from django.test import TestCase
from fcm_django.models import FCMDevice
from rest_framework.test import APIClient
from unittest import mock


class TestDirectMessageViewSetPOST(TestCase):
    """
        Test class for the POST method of the DirectMessageViewSet class.

    """

    def setUp(self):
        """
            Method to create necessary, non-unique data used by each test case in turn

        :return: None
        """
        # Sender of the message
        account_models.User.objects.create_user(email='garrett@artofvisuals.com', password='Woot',
                                                username='gallen')

        # Recipient of the message
        recipient = account_models.User.objects.create_user(email='mrtest@artofvisuals.com', password='WhoAmI',
                                                            username='aov1')

        # Recipient device
        FCMDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=recipient,
            type="ios")

    def tearDown(self):
        """
            Method to remove the non-unique data created by setUp and any extraneous data to allow for clean test cases
            on a method by method basis.

        :return: None
        """
        account_models.User.objects.all().delete()
        FCMDevice.objects.all().delete()
        PushNotificationRecord.objects.all().delete()
        DirectMessage.objects.all().delete()
        Conversation.objects.all().delete()

    def test_new_message_successful(self):
        """
            Test case to verify a new message can be created, assigned a conversation, and a push notification sent to
            the recipient.

        :return: None
        """
        sender = account_models.User.objects.get(username="gallen")
        recipient = account_models.User.objects.get(username="aov1")
        device = FCMDevice.objects.get(user=recipient)

        # Simulate auth
        token = test_helpers.get_token_for_user(sender)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Wrap the call in a mock so we aren't sending real push notifications during tests
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            # Send the message
            message_data = {
                "message": "Yo, hit me up later for some shots!"
            }

            api_response = client.post("/api/users/{}/messages".format(recipient.id), data=message_data, format="json")

            # Assert the mocked call for push notification occurred.
            p.assert_called_with(api_key=None, badge=None, data=None, icon=None,
                                 registration_ids=[device.registration_id], sound=None, title=None,
                                 body="New message from {}.".format(sender.username))

        self.assertEqual(api_response.status_code, 200)
        api_response_data = api_response.data

        self.assertEqual(api_response_data["message"], message_data["message"])
        self.assertEqual(api_response_data["sender"], sender.id)
        self.assertEqual(api_response_data["recipient"], recipient.id)
        self.assertEqual(api_response_data["index"], 1)

        # Did it create a new conversation and relate the two objects?
        self.assertTrue(Conversation.objects.filter().exists())
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(api_response_data["conversation"], Conversation.objects.first().id)

    def test_new_message_existing_conversation(self):
        """
            Unit test to verify that sending a message as part of an existing conversation tracks properly

        :return: None
        """

        sender = account_models.User.objects.get(username="gallen")
        recipient = account_models.User.objects.get(username="aov1")
        device = FCMDevice.objects.get(user=recipient)

        # Simulate auth
        token = test_helpers.get_token_for_user(sender)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Create a simple two user conversation
        conversation = Conversation.objects.create(message_count=2)
        conversation.participants = [sender.id, recipient.id]
        conversation.save()

        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=1,
                                     message="Hey man, how's it going?")
        DirectMessage.objects.create(sender=recipient, recipient=sender, conversation=conversation, index=2,
                                     message="Pretty good.")

        # Wrap the call in a mock so we aren't sending real push notifications during tests
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:
            # Send the message
            message_data = {
                "message": "Cool, cool.",
                "conversation_id": conversation.id
            }

            api_response = client.post("/api/users/{}/messages".format(recipient.id), data=message_data, format="json")

            # Assert the mocked call for push notification occurred.
            p.assert_called_with(api_key=None, badge=None, data=None, icon=None,
                                 registration_ids=[device.registration_id], sound=None, title=None,
                                 body="New message from {}.".format(sender.username))

        self.assertEqual(api_response.status_code, 200)
        api_response_data = api_response.data
        self.assertEqual(api_response_data["message"], message_data["message"])
        self.assertEqual(api_response_data["sender"], sender.id)
        self.assertEqual(api_response_data["recipient"], recipient.id)
        self.assertEqual(api_response_data["index"], 3)
        self.assertEqual(Conversation.objects.count(), 1)


class TestDirectMessageViewSetGET(TestCase):
    """
        Test class for the GET method of the DirectMessageViewSet class.

    """

    def setUp(self):
        """
            Method to create necessary, non-unique data used by each test case in turn

        :return: None
        """
        # Sender of the message
        sender = account_models.User.objects.create_user(email='garrett@artofvisuals.com', password='Woot',
                                                         username='gallen')

        # Recipient of the message
        recipient = account_models.User.objects.create_user(email='mrtest@artofvisuals.com', password='WhoAmI',
                                                            username='aov1')

        # Create a few messages, and the Conversation
        conversation = Conversation.objects.create(message_count=3)
        conversation.participants = [sender.id, recipient.id]
        conversation.save()

        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=1,
                                     message="Hey man, how's it going?")
        DirectMessage.objects.create(sender=recipient, recipient=sender, conversation=conversation, index=2,
                                     message="Pretty good.")
        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=3,
                                     message="Good to hear. Movie tonight?")

        # Recipient device
        FCMDevice.objects.create(
            registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50', user=recipient,
            type="ios")

    def tearDown(self):
        """
            Method to remove the non-unique data created by setUp and any extraneous data to allow for clean test cases
            on a method by method basis.

        :return: None
        """
        account_models.User.objects.all().delete()
        FCMDevice.objects.all().delete()
        PushNotificationRecord.objects.all().delete()
        DirectMessage.objects.all().delete()
        Conversation.objects.all().delete()

    def test_conversation_retrieval_success(self):
        """
            Unit test to verify that retrieving a Conversation works accordingly

        :return: None
        """
        sender = account_models.User.objects.get(username="gallen")
        conversation = Conversation.objects.first()

        # Simulate auth
        token = test_helpers.get_token_for_user(sender)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        api_response = client.get("/api/conversations/{}".format(conversation.id), format="json")
        self.assertEqual(api_response.status_code, 200)

        api_response_data = api_response.data["results"]

        self.assertEqual(len(api_response_data), 3)
        self.assertEqual(api_response_data[0]["message"], "Hey man, how's it going?")
        self.assertEqual(api_response_data[-1]["message"], "Good to hear. Movie tonight?")

    def test_conversation_retrieval_by_user_not_participating(self):
        """
            Test that retrieving a Conversation as a non-participating User returns an empty result list

        :return: None
        """

        # Make a new user specifically for this test
        non_participating = account_models.User.objects.create(email='gumbo@artofvisuals.com', password='haha',
                                                               username='ngumbo')
        conversation = Conversation.objects.first()

        # Simulate auth
        token = test_helpers.get_token_for_user(non_participating)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        api_response = client.get("/api/conversations/{}".format(conversation.id), format="json")
        self.assertEqual(api_response.status_code, 200)

        api_response_data = api_response.data["results"]
        self.assertEqual(len(api_response_data), 0)
