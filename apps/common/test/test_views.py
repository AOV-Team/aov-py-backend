from apps.common import views
from django.test import TestCase


class TestHandleJqueryEmptyArray(TestCase):
    """
    Test jQuery empty array fix
    """
    def test_handle_jquery_empty_array_successful(self):
        """
        Test that fix is applied

        :return: None
        """
        payload = {
            'photo_feed': ['']
        }

        fixed_payload = views.handle_jquery_empty_array('photo_feed', payload)

        self.assertEquals(fixed_payload['photo_feed'], [])

    def test_handle_jquery_empty_array_key_does_not_exist(self):
        """
        Test that fix is not applied if payload key does not exist

        :return: None
        """
        payload = {
            'photo_feed': [1, 2]
        }

        fixed_payload = views.handle_jquery_empty_array('category', payload)

        self.assertEquals(fixed_payload['photo_feed'], [1, 2])

    def test_handle_jquery_empty_array_not_empty(self):
        """
        Test that fix is not applied if array has data

        :return: None
        """
        payload = {
            'photo_feed': [1, 2]
        }

        fixed_payload = views.handle_jquery_empty_array('photo_feed', payload)

        self.assertEquals(fixed_payload['photo_feed'], [1, 2])


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
