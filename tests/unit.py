from copy import deepcopy
from uuid import uuid4

from unittest import TestCase
from unittest.mock import patch

# noinspection PyUnresolvedReferences
from sdkboil.actions import Action
# noinspection PyUnresolvedReferences
from sdkboil.object import SdkObject
# noinspection PyUnresolvedReferences
from sdkboil.exception import SdkValidationException, ConfigException, \
    UnknownContentTypeException, \
    UnknownAcceptException, \
    MissingContentTypeException, \
    MissingAcceptHeaderException
# noinspection PyUnresolvedReferences
from sdkboil.requests import Request, Response
# noinspection PyUnresolvedReferences
from sdkboil.headers import ACCEPT, STAR, CONTENT_TYPE, APPLICATION_JSON, APPLICATION_FORM_URLENCODED
# noinspection PyUnresolvedReferences
from sdkboil.api_context import Config, ApiContext
# noinspection PyUnresolvedReferences
from sdkboil.serializers import JsonSerializer, FormSerializer
# noinspection PyUnresolvedReferences
from sdkboil.deserializers import JsonDeserializer, FormDeserializer
# noinspection PyUnresolvedReferences
from sdkboil.agents import RequestsClient

from .mocks import *


class TestActions(TestCase):

    def test_action_class_declaration(self):
        with self.assertRaises(TypeError):
            class _(Action):
                pass

    def test_validation(self):
        with patch('sdkboil.actions.ValidatorFactory.make', return_value=TestValidator):
            with patch('tests.mocks.TestValidator.validate', return_value=False):
                def test_action_body_validation():
                    action = TestWriteAction(TestContext(hostname='https://testhostname.com', config=test_config))
                    with self.assertRaises(SdkValidationException):
                        action.request_body = TestSdkObject_B('a', 'b')

                def test_action_queryparams_validation():
                    action = TestReadAction(TestContext(hostname='https://testhostname.com', config=test_config))
                    with self.assertRaises(SdkValidationException):
                        action.query_parameters = {}

                def test_action_routeparams_validation():
                    action = TestReadAction(TestContext(hostname='https://testhostname.com', config=test_config))
                    with self.assertRaises(SdkValidationException):
                        action.route_parameters = {}

                def test_action_response_validation():
                    action = TestReadAction(TestContext(hostname='https://testhostname.com', config=test_config))
                    with self.assertRaises(SdkValidationException):
                        action.response_body = TestSdkObject_A('a', 'b', 'c')

                test_action_body_validation()
                test_action_queryparams_validation()
                test_action_response_validation()
                test_action_routeparams_validation()

    def test_action_run(self):
        obj_a = TestSdkObject_A('a', 'b', 'c')
        with patch('sdkboil.actions.Action._run_hooks') as mock_hooks:
            with patch('sdkboil.actions.ValidatorFactory.make', return_value=TestValidator):
                with patch('tests.mocks.TestValidator.validate', return_value=True):
                    mock_response = Response(300, {CONTENT_TYPE: APPLICATION_JSON}, {})
                    with patch('sdkboil.agents.RequestsClient.send', return_value=mock_response):
                        action = TestReadAction(TestContext(hostname='https://testhostname.com', config=test_config))
                        with self.assertRaises(TestSdkException):
                            action.run()
                        presend_call = mock_hooks.call_args_list[0]
                        failure_call = mock_hooks.call_args_list[1]
                        self.assertIn(action.presend_hooks, presend_call[0])
                        self.assertIn(action.failure_hooks, failure_call[0])
                    with patch('sdkboil.deserializers.JsonDeserializer.deserialize', return_value=obj_a):
                        mock_response = Response(200, {CONTENT_TYPE: APPLICATION_JSON}, {})
                        with patch('sdkboil.agents.RequestsClient.send', return_value=mock_response):
                            action = TestReadAction(
                                TestContext(hostname='https://testhostname.com', config=test_config))
                            response = action.run()
                            self.assertEqual(response, obj_a)
                        presend_call = mock_hooks.call_args_list[2]
                        success_call = mock_hooks.call_args_list[3]
                        self.assertIn(action.presend_hooks, presend_call[0])
                        self.assertIn(action.success_hooks, success_call[0])


class TestApiContext(TestCase):
    def test_config_validation(self):
        config = Config._init({'hostname': 'failhostname',
                               'verify_ssl': 'true'})
        with self.assertRaises(ConfigException):
            config._validate_hostname()
        with self.assertRaises(ConfigException):
            config._validate_ssl()

    def test_config_initialization(self):
        with self.assertRaises(ConfigException):
            Config._init({'hostname': 'https://testhostname.com'})
        with self.assertRaises(ConfigException):
            Config._init({'verify_ssl': True})

    def test_config_build(self):
        config = {'mode': 'live',
                  'http': {'verify_ssl': False,
                           'timeout': 10},
                  'client_id': 'mock_client_id',
                  'secret': 'mock_secret',
                  'api_version': 'v1'}
        context = ApiContext(hostname="http://testhostname.com", config=config)
        self.assertEqual(context.mode, 'live')
        self.assertEqual(context.http, {'verify_ssl': False,
                                        'timeout': 10})
        self.assertEqual(context.client_id, 'mock_client_id')
        self.assertEqual(context.secret, 'mock_secret')
        self.assertEqual(context.api_version, 'v1')
        self.assertEqual(context.client.hostname, 'http://testhostname.com')
        self.assertEqual(context.client.timeout, 10)
        self.assertEqual(context.client.verify_ssl, False)
        self.assertTrue(isinstance(context.client, RequestsClient))


class TestRequests(TestCase):
    def test_request_sending(self):
        response = TestRequestsResponse(200, {CONTENT_TYPE: APPLICATION_FORM_URLENCODED})
        req = Request(route='/resource',
                      method='GET',
                      headers={ACCEPT: STAR})
        client = RequestsClient(hostname='https://testhostname.com', config=test_config['http'])
        with patch('sdkboil.agents.requests.get', return_value=response):
            resp = client.send(req)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers, {CONTENT_TYPE: APPLICATION_FORM_URLENCODED})
            self.assertEqual(resp.body, 'abc')
            self.assertTrue(isinstance(resp, Response))

    def test_request_body_formatting(self):
        req = Request(route='/resource',
                      method='POST',
                      headers={CONTENT_TYPE: APPLICATION_JSON},
                      body={'a': 1})
        body = req._format_body()
        self.assertEqual(body, json.dumps({'a': 1}))
        req.headers = {CONTENT_TYPE: APPLICATION_FORM_URLENCODED}
        body = req._format_body()
        self.assertEqual(body, {'a': 1})
        req.headers = {CONTENT_TYPE: 'undefined'}
        with self.assertRaises(UnknownContentTypeException):
            req._format_body()
        req.headers = {}
        with self.assertRaises(MissingContentTypeException):
            req._format_body()


class TestObjects(TestCase):
    def setUp(self):
        self.obj_b = TestSdkObject_B('a1', 'a2')
        self.obj_a = TestSdkObject_A('a', 'b', {'attr_d': self.obj_b, 'attr_e': [self.obj_b]})
        self.obj_c = TestSdkCollObject_C([self.obj_a])

    def test_objects_json_serialization(self):
        json_a = JsonSerializer.serialize(self.obj_a)
        json_b = JsonSerializer.serialize(self.obj_b)

        self.assertEqual(json.loads(json_a), json_object_a)
        self.assertEqual(json.loads(json_b), json_object_b)

    def test_objects_json_deserialization(self):
        json_a = deepcopy(json_object_a)
        json_b = deepcopy(json_object_b)
        deser_a = JsonDeserializer.deserialize(TestSdkObject_A, json.dumps(json_a))
        deser_b = JsonDeserializer.deserialize(TestSdkObject_B, json.dumps(json_b))

        self.assertEqual(json.loads(JsonSerializer.serialize(self.obj_a)),
                         json.loads(JsonSerializer.serialize(deser_a)))
        self.assertEqual(json.loads(JsonSerializer.serialize(self.obj_b)),
                         json.loads(JsonSerializer.serialize(deser_b)))

    def test_collections_json_serialization(self):
        json_c = JsonSerializer.serialize(self.obj_c)
        self.assertEqual(json.loads(json_c), json_object_c)

    def test_collections_json_deserialization(self):
        json_c = deepcopy(json_object_c)
        deser_c = JsonDeserializer.deserialize(TestSdkCollObject_C, json.dumps(json_c))

        self.assertEqual(json.loads(JsonSerializer.serialize(self.obj_c)),
                         json.loads(JsonSerializer.serialize(deser_c)))


class TestCallbacks(TestCase):
    def setUp(self):
        self.handler = TestCallbackHandler(TestContext(hostname='https://testhostname.com',
                                                       config=test_config))

    def test_handler_callback_parsing(self):
        object_ = self.handler.parse({}, json.dumps({'event': 'test_event',
                                                     'object': deepcopy(
                                                         json_object_a)}).encode())
        expected = {'event': 'test_event',
                    'object': json_object_a}
        self.assertEqual(json.loads(JsonSerializer.serialize(object_)), expected)
