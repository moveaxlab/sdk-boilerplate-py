import json
# noinspection PyUnresolvedReferences
from sdkboil.actions import Action
# noinspection PyUnresolvedReferences
from sdkboil.object import SdkObject, SdkCollectionObject
# noinspection PyUnresolvedReferences
from sdkboil.exception import SdkValidationException
# noinspection PyUnresolvedReferences
from sdkboil.hooks import PresendHook, FailureHook, SuccessHook
# noinspection PyUnresolvedReferences
from sdkboil.api_context import ApiContext
# noinspection PyUnresolvedReferences
from sdkboil.callbacks import CallbackHandler


# noinspection PyUnresolvedReferences


class TestValidationError:
    def __init__(self, errors_dict):
        self.errors = errors_dict

    def to_dict(self):
        return self.errors


class TestSdkException(Exception):
    pass


class TestValidator(object):
    errors = TestValidationError({})

    def validate(self):
        return None


test_config = {'http': {"timeout": 20,
                        "verify_ssl": False}
               }


class TestContext(ApiContext):
    def __getattr__(self, item):
        return getattr(self.config, item)


class TestSdkObject_B(SdkObject):
    schema = {"attr_a": str,
              "attr_b": str,
              }
    sub_objects = {}

    def __init__(self, attr_a, attr_b):
        self.attr_a = attr_a
        self.attr_b = attr_b


class TestSdkObject_A(SdkObject):
    schema = {"attr_a": str,
              "attr_b": str,
              "attr_c": {
                  "attr_d": SdkObject,
                  "attr_e": [SdkObject]
              }}
    sub_objects = {"attr_c.attr_d": TestSdkObject_B,
                   "attr_c.attr_e": [TestSdkObject_B]}

    def __init__(self, attr_a, attr_b, attr_c):
        self.attr_a = attr_a
        self.attr_b = attr_b
        self.attr_c = attr_c


class TestSdkCollObject_C(SdkCollectionObject):
    elements_class = TestSdkObject_A


class TestSdkCallbackObject(SdkObject):
    schema = {'event': 'mock_event',
              'object': TestSdkObject_A}


class TestPresendHook(PresendHook):
    def run(self):
        pass


class TestFailureHook(FailureHook):
    def run(self):
        pass


class TestSuccessHook(SuccessHook):
    def run(self):
        pass


class TestRequestsResponse(object):
    def __init__(self, status_code, headers):
        self.status_code = status_code
        self.headers = headers
        self.content = b"abc"

    def json(self):
        return {"content": self.content.decode()}


class TestWriteAction(Action):
    request_body_class = TestSdkObject_B
    response_body_class = None
    verb = "POST"
    route = "/create"
    query_parameters_schema = {}
    route_parameters_schema = {}
    errors = {}
    presend_hooks = [TestPresendHook]
    success_hooks = [TestSuccessHook]
    failure_hooks = [TestFailureHook]
    headers = {'Content-Type' : 'application/json'}


class TestReadAction(Action):
    request_body_class = None
    response_body_class = TestSdkObject_A
    verb = "GET"
    route = "/retrieve/{resource_uuid}/{resource_uuid2}"
    query_parameters_schema = {"qparam_1": str, "qparam2": str}
    route_parameters_schema = {"resouce_uuid": str,
                               "resource_uuid2": str}
    errors = {"0404": TestSdkException}
    presend_hooks = [TestPresendHook]
    success_hooks = [TestSuccessHook]
    failure_hooks = [TestFailureHook]
    headers = {'Content-Type' : 'application/json'}

    def _get_exception(self, response):
        return self.errors["0404"]


class TestCallbackHandler(CallbackHandler):
    callbacks = {"test_event": TestSdkCallbackObject}

    def __init__(self, context):
        self.context = context

    def _verify(self, headers, raw_body):
        return True

    def _get_callback_namespace(self, raw_body):
        return json.loads(raw_body)["event"]


json_object_b = {"attr_a": "a1",
                 "attr_b": "a2"}

json_object_a = {"attr_a": "a",
                 "attr_b": "b",
                 "attr_c": {
                     "attr_d": json_object_b,
                     "attr_e": [json_object_b]
                 }}

json_object_c = [json_object_a]
