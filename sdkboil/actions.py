import json

from .utils import AbstractAttribute
from .object import SdkObject
from .exception import SdkValidationException, \
    UndefinedActionException, \
    UnknownException, \
    MissingRouteParameterException, \
    SdkHttpException
from .constants import *
from .requests import Request
from .headers import CONTENT_TYPE, ACCEPT, APPLICATION_JSON, STAR
from .hooks import PresendHook, FailureHook, SuccessHook
from .serializers import JsonSerializer
from validation.validator import ValidatorFactory


class ActionMeta(type):
    _ACTION_ATTRIBUTES = {REQUEST_BODY_CLASS: SdkObject,
                          RESPONSE_BODY_CLASS: SdkObject,
                          QUERY_PARAMETERS_SCHEMA: dict,
                          ROUTE_PARAMETERS_SCHEMA: dict,
                          ROUTE: str,
                          VERB: str,
                          ERRORS: dict,
                          PRESEND_HOOKS: list,
                          FAILURE_HOOKS: list,
                          SUCCESS_HOOKS: list,
                          HEADERS: dict}

    def __new__(mcs, name, parents, dict_):
        default_attrs = ActionMeta._ACTION_ATTRIBUTES

        parents_dicts = [dict_]
        for parent in parents:
            for class_ in parent.__mro__:
                parents_dicts.append(class_.__dict__)

        def _check_no_abs(attribute, prototype):
            return not (attribute not in prototype or prototype[attribute] is AbstractAttribute)

        def _check_type(attribute, prototype):
            return not (attribute not in prototype or prototype[attribute] and not (
                    isinstance(prototype[attribute], default_attrs[attribute]) or
                    issubclass(prototype[attribute], default_attrs[attribute])))

        if name != 'Action':
            for attr in default_attrs:
                if not any([_check_no_abs(attr, proto) for proto in parents_dicts]):
                    raise TypeError("Class {} must define attribute {}".format(name, attr))
                elif not any([_check_type(attr, proto) for proto in parents_dicts]):
                    raise TypeError("Attribute {} must be of type {}".format(attr, default_attrs[attr]))
        return super().__new__(mcs, name, parents, dict_)


class Action(metaclass=ActionMeta):
    request_body_class = AbstractAttribute
    response_body_class = AbstractAttribute
    verb = AbstractAttribute
    route = AbstractAttribute
    query_parameters_schema = AbstractAttribute
    route_parameters_schema = AbstractAttribute
    presend_hooks = []
    success_hooks = []
    failure_hooks = []

    headers = {ACCEPT: APPLICATION_JSON,
               CONTENT_TYPE: APPLICATION_JSON}

    errors = {}

    def __init__(self, context):
        self._request_body = None
        self._query_parameters = {}
        self._route_parameters = {}
        self.context = context

    @property
    def request_body(self):
        return self._request_body

    # noinspection PyUnresolvedReferences
    @request_body.setter
    def request_body(self, value):
        if not isinstance(value, self.request_body_class):
            raise ValueError("Request body must be a {} instance".format(self.request_body_class))
        self._validate_request(value)
        self._request_body = value

    @property
    def response_body(self):
        return self._response_body

    # noinspection PyUnresolvedReferences
    @response_body.setter
    def response_body(self, value):
        if not isinstance(value, self.response_body_class):
            raise ValueError("Request body must be a {} instance".format(self.response_body_class))
        self._validate_response(value)
        self._response_body = value

    @property
    def query_parameters(self):
        return self._query_parameters

    @query_parameters.setter
    def query_parameters(self, value):
        if not isinstance(value, dict):
            raise ValueError("Request body must be a dictionary")
        self._validate_query_params(value)
        self._query_parameters = value

    @property
    def route_parameters(self):
        return self._route_parameters

    @route_parameters.setter
    def route_parameters(self, value):
        if not isinstance(value, dict):
            raise ValueError("Request body must be a dictionary")
        self._validate_route_params(value)
        self._route_parameters = value

    # noinspection PyUnresolvedReferences
    def _validate_request(self, value):
        to_validate = json.loads(JsonSerializer.serialize(value))
        self._validate(to_validate, self.request_body_class.schema)

    # noinspection PyUnresolvedReferences
    def _validate_response(self, value):
        to_validate = json.loads(JsonSerializer.serialize(value))
        self._validate(to_validate, self.response_body_class.schema)

    # noinspection PyUnresolvedReferences
    def _validate_query_params(self, value):
        self._validate(value, self.query_parameters_schema)

    # noinspection PyUnresolvedReferences
    def _validate_route_params(self, value):
        self._validate(value, self.route_parameters_schema)

    def _validate(self, value, schema):
        validator = ValidatorFactory.make(schema)
        is_valid = validator.validate(value)
        if not is_valid:
            raise SdkValidationException(validator.errors.to_dict())

    def get_exception_key(self, response):
        return response.status_code

    def _get_exception(self, response):
        try:
            return self.errors[self.get_exception_key(response)]
        except KeyError:
            return UnknownException

    def _run_hooks(self, hook_list, **kwargs):
        for hook in hook_list:
            hook(context=self.context, **kwargs).run()

    def add_presend_hook(self, hook):
        if not issubclass(hook, PresendHook):
            raise ValueError("Hook not of type PresendHook")
        self.presend_hooks.append(hook)

    def add_success_hook(self, hook):
        if not issubclass(hook, SuccessHook):
            raise ValueError("Hook not of type SuccessHook")
        self.success_hooks.append(hook)

    def add_failure_hook(self, hook):
        if not issubclass(hook, FailureHook):
            raise ValueError("Hook not of type FailureHook")
        self.failure_hooks.append(hook)

    # noinspection PyUnresolvedReferences
    def _build_route(self):
        try:
            return self.route.format(**self.route_parameters)
        except KeyError:
            return MissingRouteParameterException(
                'missing parameters from {} to build route {}'.format(self.route_parameters, self.route))

    # noinspection PyUnresolvedReferences
    def run(self):
        """
        Method to send the http request and get the parsed response.
        It compiles the request, runs the presend hooks and retrieves the response.
        - If a timeout occurs, raises sdkboil.exceptions.TimeoutException
        - If a connection error occurs, raises sdkboil.exceptions.ConnectionError
        - If a response with status code > 299 is received, failure hooks are run with the proper exception retrieved
            from the errors mapping; else, defined success hooks are run
        If the actions defines a response_body_class, an instance of that class (constructed with the response body) is
        returned
        """
        request = Request(method=self.verb,
                          body=self.request_body,
                          route=self._build_route(),
                          headers=self.headers,
                          query_parameters=self.query_parameters,
                          )
        self._run_hooks(self.presend_hooks, request=request)
        response = self.context.client.send(request)
        if response.failed():
            exception = self._get_exception(response)
            exception.debug_info = self._build_debug_info(request, response)
            self._run_hooks(self.failure_hooks, request=request, response=response, exception=exception)
            raise exception
        else:
            self._run_hooks(self.success_hooks, request=request, response=response)
        return response.format(self.response_body_class, self.headers.get(ACCEPT))

    def _build_debug_info(self, request, response):
        debug_info = "Request: \n"
        debug_info += "    Route: {}\n".format(request.route)
        debug_info += "    Headers:\n"
        debug_info += self._format_debug_dict(request.headers)
        debug_info += "    Body:\n"
        debug_info += "        {}\n".format(request._format_body())
        debug_info += "    QueryParams: {}\n".format(self._format_debug_dict(request.query_parameters))
        debug_info += "Response: \n"
        debug_info += "    Status: {}\n".format(response.status_code)
        debug_info += "    Headers:\n"
        debug_info += self._format_debug_dict(response.headers)
        debug_info += "    Body:\n"
        debug_info += "        {}\n".format(response.body)
        return debug_info

    def _format_debug_dict(self, debug_dict: dict):
        return ''.join(['        {}:{}\n'.format(k, v) for k, v in debug_dict.items()])


class ActionsFactory(object):
    """
    Factory class for Action Classes. It defines a dict mapping namespaces to actual Action classes
    """
    actions = {}

    def __init__(self, context):
        self.context = context

    def make(self, action_namespace):
        """
        Method to get an Action instance from the defined namespace in the actions dict
        """
        try:
            return self.actions[action_namespace](self.context)
        except KeyError:
            raise UndefinedActionException("Action {} is undefined".format(action_namespace))
