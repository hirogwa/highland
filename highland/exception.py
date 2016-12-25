class Error(Exception):
    pass


class NoSuchEntityError(Error):
    pass


class AccessNotAllowedError(Error):
    pass


class InvalidValueError(Error):
    pass


class OperationNotAllowedError(Error):
    pass


class AuthError(Error):
    pass


class ValueError(Error):
    pass
