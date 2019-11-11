class SdkException(Exception):
    """
    Superclass for each exception raised by the Sdk. Every defined exception must inherit from this class
    to make exception handling easy
    """
    pass


# Internal Exceptions

class SdkValidationException(SdkException):
    """
    Exception wrapping a validation error occurred during sdk validation. It carries an error dict containing fields
    which failed validation and the failing rules.
    """

    def __init__(self, errors):
        self.errors = errors


class TimeoutException(SdkException):
    """
    Raised when the sending of a request fails due to a  timeout
    """
    pass


class ConnectionErrorException(SdkException):
    """
    Raised when the sending of a request fails due to a connection error
    """
    pass


class UndefinedActionException(SdkException):
    """
    Raised by the ActionsFactory when make method is called on an undefined namespace
    """
    pass


class MissingContentTypeException(SdkException):
    """
    Raised by Request instances when trying to send a body without the Content-Type header
    """
    pass


class UnknownContentTypeException(SdkException):
    """
    Raised by Request instances when sending an unknown Content-Type header
    """
    pass


class MissingAcceptHeaderException(SdkException):
    """
    Raised by Request instances when receiving a response with a body but no Accept header was set
    """
    pass


class UnknownAcceptException(SdkException):
    """
    Raised by Request instances when an Accept header was set with an unknown value
    """
    pass


class ConfigException(SdkException):
    """
    Raised by a Config instance on an invalid configuration
    """
    pass


class MissingRouteParameterException(SdkException):
    """
    Raised By Action instances where route parameters are missing
    """
    pass


class InvalidObjectClassException(SdkException):
    """
    Raised by Serializer classes when a non SdkObject v SdkCollection object subclass is given for deserialization
    """
    pass


# Http Exceptions

class SdkHttpException(SdkException):
    """
    Superclass for exceptions raised due to a received response with a status code > 299. Each subclass must define an
    error code.
    """
    error_code = None
    debug_info = None


class UnknownException(SdkHttpException):
    """
    Fallback Exception
    """
    pass
