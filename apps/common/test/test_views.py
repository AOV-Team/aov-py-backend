from apps.common import views
from django.test import TestCase


class TestRemovePksFromPayload(TestCase):
    def test_remove_pks_from_payload_successful(self):
        """
        Test that PK-related key is removed

        :return: None
        """
        payload = {
            'user_id': 1,
            'name': 'Jimmy'
        }

        sanitized = views.remove_pks_from_payload('user', payload)

        self.assertNotIn('user_id', sanitized)

    def test_remove_pks_from_payload_no_pk(self):
        """
        Test that we get same payload if no PK is found

        :return: None
        """
        payload = {
            'name': 'Travis',
            'username': 'trav'
        }

        sanitized = views.remove_pks_from_payload('user', payload)

        self.assertIn('name', sanitized)
        self.assertIn('username', sanitized)

    def test_remove_pks_from_payload_id(self):
        """
        Test that id key is removed

        :return: None
        """
        payload = {
            'id': 1,
            'name': 'Jimmy'
        }

        sanitized = views.remove_pks_from_payload('user', payload)

        self.assertNotIn('user_id', sanitized)
