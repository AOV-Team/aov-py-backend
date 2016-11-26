from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import copy

RESPONSES = {
    '200': {
        'message': 'Success',
        'userMessage': 'The action was successfully completed.'
    },
    '201': {
        'message': 'Resource successfully created.',
        'userMessage': 'Your data has been saved.'
    },
    '400': {
        'message': 'One or more required fields are missing.',
        'userMessage': 'We were unable to process your request due to an error. Please check all fields and try again.',
        'errors': []
    },
    '401': {
        'message': 'Unauthorized request',
        'userMessage': 'Sorry, you are not authorized to perform this action.',
        'errors': []
    },
    '403': {
        'message': 'Forbidden to perform action',
        'userMessage': 'You are not allowed to perform the requested action.',
        'errors': []
    },
    '404': {
        'message': 'Resource does not exist.',
        'userMessage': 'The resource you requested was not found.',
        'errors': []
    },
    '409': {
        'message': 'Resource already exists.',
        'userMessage': 'We were unable to save your data since it already exists.',
        'errors': []
    },
    '500': {
        'message': 'Internal server error',
        'userMessage': 'The server was unable to process your request due to an internal error. Please try again.',
        'errors': []
    },
    '501': {
        'message': 'Feature not yet implemented.',
        'userMessage': 'Your request is not allowed at the moment.',
        'errors': []
    }
}

# See https://github.com/RonquilloAeon/Monky-Trends-API-Guidelines
STATUS_CODES = {
    '200': status.HTTP_200_OK,
    '201': status.HTTP_201_CREATED,
    '400': status.HTTP_400_BAD_REQUEST,
    '401': status.HTTP_401_UNAUTHORIZED,
    '403': status.HTTP_403_FORBIDDEN,
    '404': status.HTTP_404_NOT_FOUND,
    '409': status.HTTP_409_CONFLICT,
    '500': status.HTTP_500_INTERNAL_SERVER_ERROR,
    '501': status.HTTP_501_NOT_IMPLEMENTED
}


def remove_pks_from_payload(model_key, payload):
    """
    Remove PK-related keys from API payload

    :param model_key: name of model as expected in payload (e.g. 'user')
    :param payload: dict to sanitize
    :return: sanitized payload - dict()
    """
    keys = [
        'id',
        model_key,
        '{}_id'.format(model_key),
        'pk'
    ]

    for key in keys:
        if key in payload:
            del payload[key]

    return payload


def get_default_response(status_code):
    """
    Retrieve a default response object that can be modified as needed
    :param status_code: the HTTP status code (string)
    :return: Rest Framework Response object
    """
    if status_code in RESPONSES:
        return Response(data=copy.copy(RESPONSES[status_code]), status=copy.copy(STATUS_CODES[status_code]))
    else:
        raise NameError('The status code {} not supported.'.format(status_code))


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
