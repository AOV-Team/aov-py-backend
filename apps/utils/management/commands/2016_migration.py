from apps.account import models as account_models
from apps.common import models as common_models
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
import collections
import csv
import datetime
import os
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
    counter = 0
    already_processed = list()

    # See if there's a record file
    if os.path.isfile('processed_images.txt'):
        already_processed = [line.rstrip('\n') for line in open('processed_images.txt')]

    with open('image.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            image_file = 'upload/' + row[5]

            # Check if image has already been imported
            if image_file in already_processed:
                continue

            # Check that we have the image file
            # If not, skip
            if not os.path.isfile(image_file):
                continue

            # Get user
            user = account_models.User.objects.filter(email=row[1]).first()

            if user:
                print('Currently processing {}'.format(image_file))

                category = photo_models.PhotoClassification.objects\
                    .filter(classification_type='category', name=row[2])\
                    .first()

                # If category does not exist, default to Other
                if not category:
                    category = photo_models.PhotoClassification.objects.get(id=8)

                # Now that know file exists and we have the image user and category, import image
                photo = Photo(open(image_file, 'rb'))
                remote_key = photo.save('u{}_{}_{}'
                                        .format(user.id, common_models.get_date_stamp_str(), photo.name),
                                        custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                # Original image url
                original_image = '{}{}'.format(settings.ORIGINAL_MEDIA_URL, remote_key)

                # Process image to save
                image = photo.compress()

                # Save image
                pic = photo_models.Photo.objects\
                    .create(user=user, image=image, location=row[7], original_image_url=original_image)
                pic.save()
                pic.category = [category]
                pic.save()

                # Record that image has been uploaded in case import blows up we can start again and not dupe images
                f = open('processed_images.txt', 'a+')
                f.write(image_file + '\n')
                f.close()

                counter += 1

    print('Imported {} images'.format(counter))


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
