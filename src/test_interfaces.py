# pylint: disable=protected-access,invalid-name,line-too-long
"""Module for testing interfaces"""

from unittest import TestCase, IsolatedAsyncioTestCase, mock
from structlog.testing import capture_logs
import requests
import requests_mock

from interfaces import HttpsInterface, WebsocketSubscription, WebsocketInterface
from cache import Cache
from log import logger


class TestConfiguration(TestCase):
    """Tests HttpsInterface interface."""

    def setUp(self):
        """Set up dummy interface for us."""
        self.maxDiff = None
        self.url = "https://test.com/?apikey=123456"
        self.interface = HttpsInterface(self.url, 1, 2)

    def test_url_attribute(self):
        self.assertEqual(self.url, self.interface.url)

    def test_connect_timeout_attribute(self):
        self.assertEqual(1, self.interface.connect_timeout)

    def test_response_timeout_attribute(self):
        self.assertEqual(2, self.interface.response_timeout)

    def test_session_attribute(self):
        self.assertEqual(type(self.interface.session), requests.Session)

    def test_logger_attribute(self):
        self.assertEqual(self.interface._logger, logger)

    def test_logger_metadata(self):
        """Validate metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {'component': 'HttpsCollector', 'url': 'test.com'}
        self.assertEqual(self.interface._logger_metadata, expected_metadata)

    def test_cache_attribute(self):
        self.assertEqual(type(self.interface.cache), Cache)

    def test_return_and_validate_post_request_method_200(self):
        with requests_mock.Mocker(session=self.interface.session) as m:
            m.post(self.url, text="Ok", status_code=200)
            payload = {
                "jsonrpc": "1.0",
                "id": "exporter",
                "method": "getnetworkinfo"
            }
            result = self.interface._return_and_validate_post_request(payload)
            self.assertEqual(result, "Ok")
            self.assertEqual(m.called, True)
            self.assertEqual(m.call_count, 1)

    def test_return_and_validate_post_request_method_non_200(self):
        with requests_mock.Mocker(session=self.interface.session) as m:
            m.post(self.url, text="Ok", status_code=500)
            payload = {
                "jsonrpc": "1.0",
                "id": "exporter",
                "method": "getnetworkinfo"
            }
            result = self.interface._return_and_validate_post_request(payload)
            self.assertEqual(result, None)
            self.assertEqual(m.called, True)
            self.assertEqual(m.call_count, 1)


class TestWebSocketSubscription(TestCase):
    """Tests the web socket subscription class"""

    def setUp(self):
        self.url = "wss://test.com/?apikey=123456"
        self.client_params = {"dummy": "data"}
        self.web_sock_sub = WebsocketSubscription(
            self.url, self.client_params)

    def test_url_attribute(self):
        """Tests the url arg is set to the _url attribute correctly"""
        self.assertEqual(self.url, self.web_sock_sub._url)

    def test_logger_metadata(self):
        """Validate metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {
            'component': 'WebsocketSubscription', 'url': 'test.com'}
        self.assertEqual(self.web_sock_sub._logger_metadata, expected_metadata)


class TestWebSocketInterface(IsolatedAsyncioTestCase):
    """Tests the web socket interface class"""

    def setUp(self):
        self.url = "wss://test.com/?apikey=123456"
        self.client_params = {"ping_timeout": 7}
        self.web_sock_interface = WebsocketInterface(
            self.url, **self.client_params)

    def test_load_and_validate_json_key_valid_json(self):
        """Tests that the correct value for a key is returned when providing valid json"""
        message = '{"result": "valid"}'
        key = 'result'
        result = self.web_sock_interface._load_and_validate_json_key(
            message, key)
        self.assertEqual("valid", result)

    def test_load_and_validate_json_key_invalid_json(self):
        """Tests that None type is returned when providing an invalid json message"""
        # json message is missing quotes around invalid
        message = '{"result": invalid}'
        key = 'result'
        result = self.web_sock_interface._load_and_validate_json_key(
            message, key)
        self.assertEqual(None, result)

    def test_load_and_validate_json_key_invalid_json_error_log(self):
        """Tests that an error is logged when the json message does not contain the specified key"""
        message = '{"wrongkey": "valid"}'
        key = "result"
        with capture_logs() as captured:
            self.web_sock_interface._load_and_validate_json_key(
                message, key)
        self.assertTrue(any([log['log_level'] == "error" for log in captured]))

    def test_query_call(self):
        """Tests that the query function calls the _query function with correct args"""
        with mock.patch('interfaces.WebsocketInterface._query') as mocked_query:
            self.web_sock_interface.query("payload", False)
            mocked_query.assert_called_once_with("payload", False)

    async def test_async_query_method_return(self):
        """Tests that the value in the result key from the websocket response is returned"""
        with mock.patch('interfaces.connect', autospec=True) as websocket:
            websocket.return_value.__aenter__.return_value.recv.return_value = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
            resp_data = await self.web_sock_interface._query("payload", False)
            self.assertEqual(-19, resp_data)

    async def test_async_query_method_return_skip_checks(self):
        """Tests that the value in the result key from the websocket response is returned
        when skip_checks is true"""
        with mock.patch('interfaces.connect', autospec=True) as websocket:
            websocket.return_value.__aenter__.return_value.recv.return_value = '{"result":"dummy data"}'
            resp_data = await self.web_sock_interface._query("payload", True)
            self.assertEqual("dummy data", resp_data)
