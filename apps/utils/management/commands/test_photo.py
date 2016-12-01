from apps.utils.commands import TermColor
from django.core.management import BaseCommand
from rest_framework.test import APIClient


def test_photo(access_token, filename):
    """

    :param access_token: User access token
    :param filename: Name of file to upload
    :return: None
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + access_token)

    with open(filename, 'rb') as image:
        payload = {
            'category': 8,
            'image': image
        }

        request = client.post('/api/photos', data=payload, format='multipart')

    result = request.data
    print(TermColor.OKBLUE + str(result) + TermColor.ENDC)


class Command(BaseCommand):
    help = 'Test API endpoints with photo content'

    def add_arguments(self, parser):
        parser.add_argument('-a',
                            action='store',
                            dest='token',
                            default=False,
                            help='Access token')
        parser.add_argument('-e',
                            action='store',
                            dest='endpoint',
                            default='photo',
                            help='Endpoint (photo|), default "photo"')
        parser.add_argument('-p',
                            action='store',
                            dest='filename',
                            default=False,
                            help='Path to photo')

    def handle(self, *args, **options):
        endpoint = options['endpoint']
        filename = options['filename']
        token = options['token']

        if endpoint == 'photo':
            test_photo(token, filename)
