from apps.account import models as account_models
from apps.common.test import helpers as test_helpers
from django.test import TestCase
from rest_framework.test import APIClient


class TestBlockUserViewSetPOST(TestCase):
    """
    Test /api/users POST (user creation)
    """

    def setUp(self):
        """
            Create the test data

        :return: None
        """
        account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        account_models.User.objects.create_user(email='gallen@mypapaya.io', password='pass', username='aov_1')


    def tearDown(self):
        """
            Remove test data after each case

        :return: None
        """

        account_models.User.objects.all().delete()
        account_models.Blocked.objects.all().delete()


    def test_block_new_successful(self):
        """
        Make sure adding a new user to the blocked list works

        :return: None
        """
        user = account_models.User.objects.get(username="aov_hov")
        blocked = account_models.User.objects.get(username="aov_1")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.post("/api/users/{}/blocked".format(user.id), data={"user_id": blocked.id}, format="json")

        self.assertEqual(response.status_code, 200)

        self.assertTrue(account_models.Blocked.objects.filter(blocked_by=user).exists())
        self.assertEqual(account_models.Blocked.objects.filter(blocked_by=user).count(), 1)

    def test_blocked_existing_successful(self):
        """
        Test the attempting to block a blocked user does nothing

        :return: None
        """

        user = account_models.User.objects.get(username="aov_hov")
        blocked = account_models.User.objects.get(username="aov_1")

        # Create the Blocked entry ahead of time
        account_models.Blocked.objects.create(user=blocked, blocked_by=user)

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.post("/api/users/{}/blocked".format(blocked.id), data={"user_id": blocked.id}, format="json")

        self.assertEqual(response.status_code, 200)

        self.assertTrue(account_models.Blocked.objects.filter(blocked_by=user).exists())
        self.assertEqual(account_models.Blocked.objects.filter(blocked_by=user).count(), 1)

    def test_removing_block_on_a_user(self):
        """
        Test that requesting to remove a block on a user works

        :return: None
        """

        blocked_user = account_models.User.objects.get(username="aov_1")
        blocker = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(blocker)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.post("/api/users/{}/blocked".format(blocker.id),
                               data={"remove": True, "user_id": blocked_user.id}, format="json")

        self.assertEqual(response.status_code, 200)

        # Verify the Blocked entry has been removed
        self.assertFalse(account_models.Blocked.objects.filter(user=blocked_user, blocked_by=blocker).exists())


class TestBlockViewSetGET(TestCase):
    """
    Class to test the retrieval of blocked Users by their blocking user

    """

    def setUp(self):
        """
            Create the test data

        :return: None
        """
        blocking = account_models.User.objects.create_user(email='mrtest@mypapaya.io', password='pass', username='aov_hov')
        blocked = account_models.User.objects.create_user(email='gallen@mypapaya.io', password='pass', username='aov_1')
        account_models.Blocked.objects.create(user=blocked, blocked_by=blocking)


    def tearDown(self):
        """
        Remove the test data after each case

        :return: None
        """

        account_models.Blocked.objects.all().delete()
        account_models.User.objects.all().delete()


    def test_get_blocked_users_as_blocker_successful(self):
        """
        Test that I can get a list of Users I have blocked

        :return: None
        """

        user = account_models.User.objects.get(username="aov_hov")

        # Simulate auth
        token = test_helpers.get_token_for_user(user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.get("/api/users/{}/blocked".format(user.id), format="json")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "aov_1")

    def test_get_blocked_users_as_non_blocker_successful(self):
        """
        Verify an empty list when attempting to see someone else's blocked list

        :return:
        """
        blocking_user = account_models.User.objects.get(username="aov_hov")
        accessing_user = account_models.User.objects.get(username="aov_1")

        # Simulate auth
        token = test_helpers.get_token_for_user(accessing_user)

        # Get data from endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = client.get("/api/users/{}/blocked".format(blocking_user.id), format="json")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["results"]), 0)
