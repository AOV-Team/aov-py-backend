from django.test import TestCase
from django.conf import settings
from django.utils.module_loading import import_module
from rest_framework.authtoken.models import Token
import fnmatch
import glob
import os
import shutil


class SessionTestCase(TestCase):
    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key


def clear_directory(path, pattern='*'):
    """
    Delete files in a directory or directories based on a pattern

    :param path: path to dir
    :param pattern: pattern to glob with
    :return: None
    """
    for f in glob.glob(os.path.join(path, pattern)):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def find_file_by_pattern(path, pattern):
    """
    Find files in specified path that match given pattern

    :param path: directory to search
    :param pattern: UNIX glob-style pattern
    :return: list of matched files or None
    """
    matched_files = list()

    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            matched_files.append(file)

    return matched_files if len(matched_files) > 0 else None


def get_token_for_user(user):
    """
    Create/get a token for a user. Simulates authentication.

    :param user: Usr object
    :return: token
    """
    token = Token.objects.get_or_create(user=user)
    return token[0].key
