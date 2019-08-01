from apps.account import models as account_models
from apps.common import mailer
from dbmail.models import MailTemplate
from django.test import TestCase, override_settings
from unittest import mock


@override_settings(CELERY_TASK_ALWAYS_EAGER=True,
                   EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend")
class TestMailer(TestCase):
    def setUp(self):
        """
        Set up test data

        :return: None
        """
        MailTemplate.objects.create(
            name='Test email',
            subject='Unit Test email',
            message='Hello world',
            slug='welcome',
            is_html=False
        )

    def test_send_transactional_email_successful(self):
        """
        Test that we can send a transactional email

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov_hov')

        with mock.patch('django.core.mail.backends.dummy.EmailBackend.send_messages') as p:
            mailer.send_transactional_email(user, 'welcome')

            self.assertTrue(p.called)

    @override_settings(EMAIL_BACKEND="")
    def test_send_transactional_email_no_backend(self):
        """

        :return: None
        """
        user = account_models.User.objects.create_user(email='test@test.com', username='aov_hov')

        with self.assertRaises(mailer.CommunicationException):
            mailer.send_transactional_email(user, 'welcome')
