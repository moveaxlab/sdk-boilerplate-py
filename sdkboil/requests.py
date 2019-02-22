from .serializers import _get_serializer
from .deserializers import _get_deserializer
from .headers import CONTENT_TYPE


class Request(object):
    """
    Wrapper class for an http request. It sends http requests using the python requests module
    """

    def __init__(self, route, method, headers, body=None, query_parameters=None):
        self.route = route
        self.method = method
        self.headers = headers
        self.body = body
        self.query_parameters = query_parameters

    def _format_body(self):
        return _get_serializer(self.headers.get(CONTENT_TYPE)).serialize(self.body)


class Response(object):
    """
    Wrapper class for http responses
    """

    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def failed(self):
        return self.status_code > 299

    def format(self, class_=None, content_type=None):
        content_type = content_type or self.headers.get(CONTENT_TYPE)
        if not class_:
            return self.body
        else:
            return _get_deserializer(content_type).deserialize(class_, self.body)
