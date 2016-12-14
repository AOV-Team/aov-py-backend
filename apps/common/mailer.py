from dbmail import send_db_mail


class CommunicationException(Exception):
    """
    Exception that is raised if there's a problem with sending a piece of communication to a user(s)
    """
    def __init__(self, message):
        super(CommunicationException, self).__init__(message)


def send_transactional_email(user, slug, **data):
    """
    Send a transactional email message to a user
    :param user: User object
    :param slug: Mail template slug
    :param data: data dict to pass to template
    :return:
    """
    try:
        send_db_mail(slug, user.email, data)
    except ImportError:
        raise CommunicationException('Django mail settings may be incorrectly configured.')
