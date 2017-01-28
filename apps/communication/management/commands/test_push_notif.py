from django.core.management import BaseCommand
from push_notifications.models import APNSDevice


class Command(BaseCommand):
    help = 'Test sending out push notifications'

    def handle(self, *args, **options):
        """
        http://django-db-mailer.readthedocs.io/providers.html

        :param args:
        :param options:
        :return:
        """
        device = APNSDevice.objects\
            .get(registration_id='1D2440F1F1BB3C1D3953B40A85D02403726A48828ACF92EDD5F17AAFFBFA8B50')

        device.send_message('This is a test')
