from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from apps.communication.models import DirectMessage, PushNotificationRecord, Conversation
from django.test import TestCase
from fcm_django.models import FCMDevice
from rest_framework.test import APIClient


class TestConversationViewSetGET(TestCase):
    """
        Test class for the GET method of the ConversationViewSet class.

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
        conversation.participants.set([sender.id, recipient.id])
        conversation.save()

        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=1,
                                     message="Hey man, how's it going?")
        DirectMessage.objects.create(sender=recipient, recipient=sender, conversation=conversation, index=2,
                                     message="Pretty good.")
        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=3,
                                     message="Good to hear. Movie tonight?")

    def tearDown(self):
        """
            Method to remove the non-unique data created by setUp and any extraneous data to allow for clean test cases
            on a method by method basis.

        :return: None
        """
        account_models.User.objects.all().delete()
        DirectMessage.objects.all().delete()
        Conversation.objects.all().delete()

    def test_conversation_retrieval_success(self):
        """
            Unit test to verify that retrieving a Conversation works accordingly

        :return: None
        """
        user = account_models.User.objects.get(username="gallen")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        api_response = client.get("/api/users/{}/conversations".format(user.id), format="json")
        self.assertEqual(api_response.status_code, 200)

        api_response_data = api_response.data["results"]

        self.assertEqual(len(api_response_data), 1)
        self.assertEqual(api_response_data[0]["latest"]["message"], "Good to hear. Movie tonight?")
        self.assertEqual(api_response_data[0]["message_count"], 3)

    def test_conversation_retrieval_by_user_not_participating(self):
        """
            Test that retrieving a Conversation as a non-participating User returns an empty result list

        :return: None
        """

        # Make a new user specifically for this test
        non_participating = account_models.User.objects.create(email='gumbo@artofvisuals.com', password='haha',
                                                               username='ngumbo')

        # Simulate auth
        token = test_helpers.get_token_for_user(non_participating)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        api_response = client.get("/api/users/{}/conversations".format(non_participating.id), format="json")
        self.assertEqual(api_response.status_code, 200)

        api_response_data = api_response.data["results"]
        self.assertEqual(len(api_response_data), 0)


    def test_conversation_retrieval_by_participant_list(self):
        """
            Unit test to verify that requesting conversations based on it's participants works correctly

        :return: None
        """
        # Make a new user specifically for this test
        participant = account_models.User.objects.create(email='gumbo@artofvisuals.com', password='haha',
                                                         username='ngumbo')
        user = account_models.User.objects.get(username="gallen")

        # Add the new participant to the conversation
        conversation = Conversation.objects.first()
        conversation.participants.add(participant)
        conversation.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(participant)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        api_response = client.get("/api/conversations?participants={}&participants={}".format(participant.id, user.id),
                                  format="json")
        self.assertEqual(api_response.status_code, 200)

        api_response_data = api_response.data["results"]
        self.assertEqual(len(api_response_data), 1)


class TestConversationViewSetDELETE(TestCase):
    """
        Class to test the deletion of a Conversation by a user

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
        conversation.participants.set([sender.id, recipient.id])
        conversation.save()

        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=1,
                                     message="Hey man, how's it going?")
        DirectMessage.objects.create(sender=recipient, recipient=sender, conversation=conversation, index=2,
                                     message="Pretty good.")
        DirectMessage.objects.create(sender=sender, recipient=recipient, conversation=conversation, index=3,
                                     message="Good to hear. Movie tonight?")

    def tearDown(self):
        """
            Method to remove the non-unique data created by setUp and any extraneous data to allow for clean test cases
            on a method by method basis.

        :return: None
        """
        account_models.User.objects.all().delete()
        DirectMessage.objects.all().delete()
        Conversation.objects.all().delete()

    def test_delete_conversation_with_user_left(self):
        """
            Unit test to verify that if I delete a conversation, it doesn't delete it for other participants.

        :return: None
        """

        user = account_models.User.objects.get(username="gallen")
        conversation = Conversation.objects.get(participants=user)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        api_response = client.delete("/api/users/{}/conversations/{}".format(user.id, conversation.id),
                                     format="json")

        self.assertEqual(api_response.status_code, 200)

        # Retrieve the updated Conversation
        conversation = Conversation.objects.get(id=conversation.id)

        self.assertFalse(conversation.participants.filter(id=user.id).exists())

    def test_delete_conversation_as_last_user(self):
        """
            Verifies a complete removal of the Conversation and related messages if the last participant deletes the
            conversation

        :return: None
        """

        user = account_models.User.objects.get(username="gallen")
        conversation = Conversation.objects.get(participants=user)
        conversation.participants.clear()
        conversation.save()
        conversation.participants.add(user)
        conversation.save()

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        api_response = client.delete("/api/users/{}/conversations/{}".format(user.id, conversation.id),
                                     format="json")

        self.assertEqual(api_response.status_code, 200)

        # Retrieve the updated Conversation
        conversation = Conversation.objects.filter(id=conversation.id)

        self.assertFalse(conversation.exists())
        self.assertEqual(len(DirectMessage.objects.all()), 0)
