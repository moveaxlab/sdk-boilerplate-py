import requests

from abc import ABC, abstractmethod

from .exception import TimeoutException, ConnectionErrorException
from .requests import Response


class Client(ABC):
    """
    Abstract class which wraps a specific user agent. It takes the sdk configuration and exposes the send method
    which takes the Sdk Request object as input and calls the related low level user agent formatting parameters
    """

    def __init__(self, hostname, config):
        self.hostname = hostname
        self.timeout = config['timeout']
        self.verify_ssl = config['verify_ssl']

    @abstractmethod
    def send(self, request):
        raise NotImplemented("Subclasses must impelemt this method")


class RequestsClient(Client):
    def send(self, request):
        agent_arguments = self._get_request_params(request)
        try:
            response = getattr(requests, request.method.lower())(**agent_arguments)
        except requests.Timeout:
            raise TimeoutException
        except (requests.ConnectionError, requests.ConnectTimeout):
            raise ConnectionErrorException
        return Response(response.status_code, response.headers, response.content.decode())

    def _get_request_params(self, request):
        params = {'url': '{}{}'.format(self.hostname, request.route),
                  'headers': request.headers,
                  'verify': self.verify_ssl}
        if request.query_parameters:
            params['params'] = request.query_parameters
        if request.body:
            params['data'] = request._format_body()
        return params
