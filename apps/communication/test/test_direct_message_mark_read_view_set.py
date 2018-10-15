from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import DirectMessage, PushNotificationRecord, Conversation
from apps.communication.serializers import DirectMessageSerializer
from django.test import TestCase
from fcm_django.models import FCMDevice
from rest_framework.test import APIClient
from unittest import mock


class TestDirectMessageMarkReadViewSetPOST(TestCase):
    """
        Test class for the POST method of the DirectMessageViewSet class.

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
        FCMDevice.objects.create(registration_id="1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A",
                                 type="ios", user=sender)

    def tearDown(self):
        """
            Method to remove the non-unique data created by setUp and any extraneous data to allow for clean test cases
            on a method by method basis.

        :return: None
        """
        account_models.User.objects.all().delete()
        account_models.Blocked.objects.all().delete()
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
        device = FCMDevice.objects.get(user=sender)
        message = DirectMessage.objects.first()

        # Simulate auth
        token = test_helpers.get_token_for_user(recipient)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Wrap the call in a mock so we aren't sending real push notifications during tests
        with mock.patch('fcm_django.fcm.fcm_send_bulk_message') as p:

            api_response = client.post("/api/users/{}/messages/{}/read".format(sender.id, message.id), format="json")

            push_data = DirectMessageSerializer(DirectMessage.objects.filter(id=message.id).first()).data

            # Assert the mocked call for push notification occurred.
            p.assert_called_with(api_key=None, badge=None, data=push_data, icon=None,
                                 registration_ids=[device.registration_id], sound=None, title=None,
                                 body=None)

        self.assertEqual(api_response.status_code, 200)
        api_response_data = api_response.data

        self.assertEqual(api_response_data["message"], message.message)
        self.assertEqual(api_response_data["sender"], sender.id)
        self.assertEqual(api_response_data["recipient"], recipient.id)
        self.assertTrue(api_response_data["read"])
