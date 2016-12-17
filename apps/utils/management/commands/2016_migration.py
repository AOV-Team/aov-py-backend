from apps.account import models as account_models
from apps.common import models as common_models
from apps.photo import models as photo_models
from apps.photo.photo import Photo
from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
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

    return feed_photos


def import_feed():
    """
    Add images to feed. Run image import before running this file

    :return: None
    """
    feed_images = list()

    # Load data
    with open('feed_images.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            feed_images.append([int(row[0]), int(row[1])])

    # Sort images into proper order that they were added into the feed
    feed_images = sorted(feed_images, key=lambda x: x[1])

    # Add photos to AOV feed
    feed = photo_models.PhotoFeed.objects.get(id=1)

    for image in feed_images:
        photo = photo_models.Photo.objects.get(id=image[0])
        photo.photo_feed = [feed]
        photo.save()


def import_images():
    """
    Import images from old DB

    :return: None
    """
    counter = 0
    already_processed = list()

    # Get feed data
    feed_data = get_feed_data()

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

                # Save feed data for importing later if image is in feed
                feed_index = feed_data[row[0]] if row[0] in feed_data else None

                if feed_index:
                    f = open('feed_images.csv', 'a+')
                    # New photo id, feed index
                    f.write('{},{}\n'.format(pic.id, feed_index))
                    f.close()

                counter += 1

    print('Imported {} images'.format(counter))


def import_users():
    """
    Import users from old db

    :return: None
    """
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


class Command(BaseCommand):
    help = 'Migrate from PHP backend to Django'

    def add_arguments(self, parser):
        help_text = 'Name of action to perform (feed|user|photo)'

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
            if action == 'user':
                import_users()
            elif action == 'photo':
                import_images()
            if action == 'feed':
                import_feed()
            else:
                print('Invalid command')
