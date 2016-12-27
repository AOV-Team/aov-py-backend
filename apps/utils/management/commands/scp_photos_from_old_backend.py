from django.core.management import BaseCommand
import csv
import datetime
import os
import subprocess


def scp_images():
    """
    Copy images from old server

    :return: None
    """
    counter = 0
    already_processed = list()

    # See if there's a record file
    if os.path.isfile('processed_images.txt'):
        already_processed = [line.rstrip('\n') for line in open('processed_images.txt')]

    with open('image.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            local_image_file_path = 'upload/' + row[5]

            # Check if image has already been migrated
            if local_image_file_path in already_processed:
                continue

            commands = ['scp', '-r',
                        'ec2-user@35.161.253.169:"\'/var/www/html/ArtOfVisuals/upload/{}\'"'.format(row[5]), 'upload']

            print(commands)
            subprocess.call(commands)

            counter += 1

    print('Copied {} images'.format(counter))


class Command(BaseCommand):
    help = 'Copy photos from old backend'

    def handle(self, *args, **options):
        today = int(str(datetime.datetime.today().date()).replace('-', ''))

        # Command expires on Mar 1, 2017
        if today <= 20170301:
            scp_images()
        else:
            print('Command expired')
