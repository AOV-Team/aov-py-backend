from apps.account import models as account_models
from apps.common import mailer
from dbmail.models import MailTemplate
from django.core import mail
from django.test import TestCase


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

        mailer.send_transactional_email(user, 'welcome')

        self.assertEquals(len(mail.outbox), 1)

    def test_send_transactional_email_no_backend(self):
        """

        :return: None
        """
        with self.settings(EMAIL_BACKEND=''):
            user = account_models.User.objects.create_user(email='test@test.com', username='aov_hov')

            with self.assertRaises(mailer.CommunicationException):
                mailer.send_transactional_email(user, 'welcome')
