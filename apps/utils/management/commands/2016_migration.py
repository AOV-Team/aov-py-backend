from apps.account import models as account_models
from apps.photo import models as photo_models
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
import collections
import csv
import datetime
import random
import string


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_feed_data():
    """
    Create a dict containing the old photo id (key) and feed id (value). Use this to add photos to the new feed in the
    right order

    :return: dict containing feed data
    """
    feed_photos = dict()

    with open('feed.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            feed_photos[row[1]] = row[0]

    # ordered_feed_photos = collections.OrderedDict()
    #
    # for i in sorted(feed_photos.items(), key=lambda x: int(x[1])):
    #     ordered_feed_photos[i[0]] = i[1]
    #
    # print(ordered_feed_photos)

    return feed_photos


def import_users():
    with open('user.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            # Handle age
            try:
                age = int(row[7])
            except ValueError:
                age = None

            # Handle name
            # Split by first space. First item is set as first name
            # Subsequent items set as last name
            name = row[1].split(' ')
            first_name = name[0]
            last_name = ''

            if len(name) > 1:
                counter = 1

                while counter < len(name):
                    last_name += name[counter] + ' '
                    counter += 1

            last_name = last_name.strip()

            # Attempt to create user
            # If username already exists, append a random string to end of username and create user
            try:
                account_models.User.objects\
                    .create_user(age=age, created_at=row[8], email=row[2], first_name=first_name,
                                 last_name=last_name, location=row[4], social_name=row[5], username=row[5])
            except IntegrityError as e:
                if '(username)' in str(e):
                    account_models.User.objects \
                        .create_user(age=age, created_at=row[8], email=row[2], first_name=first_name,
                                     last_name=last_name, location=row[4], social_name=row[5],
                                     username=row[5] + id_generator())


def import_images():
    pass


class Command(BaseCommand):
    help = 'Migrate from PHP backend to Django'

    def add_arguments(self, parser):
        help_text = 'Name of action to perform (pp[prep photo data - merge feed and image files]|user|photo)'

        parser.add_argument('-a',
                            action='store',
                            dest='action',
                            default=False,
                            help=help_text)

    def handle(self, *args, **options):
        action = options['action']
        today = int(str(datetime.datetime.today().date()).replace('-', ''))

        # Command expires on Dec 25, 2016
        if today <= 20161225:
            if action == 'pp':
                get_feed_data()
            elif action == 'user':
                import_users()
            elif action == 'photo':
                import_images()
            else:
                print('Invalid command')
