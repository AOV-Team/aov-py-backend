class ForbiddenValue(ValueError):
    """
    Exception for when a forbidden value is found
    """
    pass


class OverLimitException(ValueError):
    """
    Exception for when item limit has been surpassed
    """
    pass

class MissingRequiredFieldException(Exception):
    """
    Exception to be used in API views for when a required field is missing in the request
    """
    pass
