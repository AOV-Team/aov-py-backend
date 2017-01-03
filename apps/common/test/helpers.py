from rest_framework.authtoken.models import Token
import fnmatch
import glob
import os


def clear_directory(path, pattern='*'):
    """
    Delete files in a directory based on a pattern
    :param path: path to dir
    :param pattern: pattern to glob with
    :return: None
    """
    for f in glob.glob(os.path.join(path, pattern)):
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
