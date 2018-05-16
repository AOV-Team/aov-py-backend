from apps.utils.commands import TermColor
from django.core.management import BaseCommand
import json
import requests
import subprocess
import os


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def test_photo(access_token, filename, server_prefix):
    """

    :param access_token: User access token
    :param filename: Name of file to upload
    :return: None
    """
    headers = {"authorization": "Token {}".format(access_token)}
    payload = {'category': 8}

    image_size = file_size(filename)

    if image_size:
        if image_size <= "10.0 MB":
            with open(filename, 'rb') as image:
                image_file = {'image': image}

                request = requests.post(server_prefix + '/api/photos', data=payload, files=image_file, headers=headers)

                result = request.json()
                print(TermColor.OKBLUE + json.dumps(result) + TermColor.ENDC)
        else:
            result = subprocess.call(["curl", "-F", "category=8", "-F", "image=@{}".format(filename), "-H",
                             "Authorization: Token {}".format(access_token), "{}/api/photos".format(server_prefix)])

            print(TermColor.OKBLUE + str(result) + TermColor.ENDC)
    else:
        print(TermColor.FAIL + "404: File Not Found" + TermColor.ENDC)


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
        parser.add_argument('-s',
                            action="store",
                            dest="server",
                            default="local",
                            help="Server name to direct the request towards")

    def handle(self, *args, **options):
        endpoint = options['endpoint']
        filename = options['filename']
        token = options['token']
        server = options['server']

        server_lookup = {
            "staging": "https://staging.artofvisuals.com",
            "local": "http://localhost:8000"
        }

        if endpoint == 'photo':
            test_photo(token, filename, server_lookup[server])
