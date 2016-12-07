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
