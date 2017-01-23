from apps.utils.commands import TermColor
from dbmail import send_db_push
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Test sending out push notifications'

    def handle(self, *args, **options):
        """
        http://django-db-mailer.readthedocs.io/providers.html

        :param args:
        :param options:
        :return:
        """
        send_db_push()
