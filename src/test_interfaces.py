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
        """Tests url attribute is set as expected"""
        self.assertEqual(self.url, self.interface.url)

    def test_connect_timeout_attribute(self):
        """Tests connect_timeout attribute is set as expected"""
        self.assertEqual(1, self.interface.connect_timeout)

    def test_response_timeout_attribute(self):
        """Tests response_timeout attribute is set as expected"""
        self.assertEqual(2, self.interface.response_timeout)

    def test_session_attribute(self):
        """Tests session attribute is set as expected"""
        self.assertEqual(type(self.interface.session), requests.Session)

    def test_logger_attribute(self):
        """Tests logger attribute is setup as expected"""
        self.assertEqual(self.interface._logger, logger)

    def test_logger_metadata(self):
        """Validate metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {'component': 'HttpsCollector', 'url': 'test.com'}
        self.assertEqual(self.interface._logger_metadata, expected_metadata)

    def test_cache_attribute(self):
        """Tests cache attribute is set as expected"""
        self.assertEqual(type(self.interface.cache), Cache)

    def test_return_and_validate_post_request_method_200(self):
        """Tests the post request method is called once and returns Ok for 200 status code"""
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
        """Tests the post request method is called once and returns None for 500 status code"""
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
        self.client_params = {"ping_timeout": 3}
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

    def test_client_params(self):
        """Tests that the client params attribute is set correctly"""
        self.assertEqual(self.client_params,
                         self.web_sock_interface._client_parameters)

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
        self.assertTrue(any(log['log_level'] == "error" for log in captured))

    def test_load_and_validate_json_key_valid_json_no_error_log(self):
        """Tests that no error is logged when the json message does contain the specified key"""
        message = '{"result": "valid"}'
        key = "result"
        with capture_logs() as captured:
            self.web_sock_interface._load_and_validate_json_key(
                message, key)
        self.assertFalse(
            any(log['log_level'] == "error" for log in captured))

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

    async def test_async_query_send(self):
        """Tests that the websocket send method is called with the correct args"""
        with mock.patch('interfaces.connect', autospec=True) as websocket:
            send_mock = mock.AsyncMock()
            websocket.return_value.__aenter__.return_value.recv.return_value = '{"result":"dummy data"}'
            websocket.return_value.__aenter__.return_value.send = send_mock
            await self.web_sock_interface._query("payload", True)
            send_mock.assert_awaited_once_with('"payload"')

    async def test_async_query_timeout_return(self):
        """Tests that the query method returns None on a websocket timeout"""
        with mock.patch('interfaces.connect', autospec=True) as websocket:
            # Convert websocket send method from async to regular mock since wait_for will be mocked
            websocket.return_value.__aenter__.return_value.send = mock.Mock()
            with mock.patch('interfaces.asyncio.wait_for', side_effect=TimeoutError):
                result = await self.web_sock_interface._query("payload", True)
                self.assertEqual(None, result)

    def test_cache_query_retrieve_valid_key(self):
        """Tests that the retrieve_key_value method is called and returns a value if the key is in the cache"""
        with mock.patch('interfaces.Cache') as mocked_cache:
            mocked_cache.is_cached.return_value = True
            mocked_cache.retrieve_key_value.return_value = 'value'
            self.web_sock_interface.cache = mocked_cache
            result = self.web_sock_interface.cached_query('key')
            self.assertEqual('value', result)

    def test_cache_query_retrieve_invalid_key(self):
        """Tests that the query method is called for a key not in the cache"""
        with mock.patch('interfaces.WebsocketInterface.query') as mocked_query:
            self.web_sock_interface.cached_query('key', False)
            mocked_query.assert_called_once_with('key', False)

    def test_cache_query_retrieve_invalid_key_added_to_cache(self):
        """Tests that the method adds key to cache if it doesn't already exist"""
        with mock.patch('interfaces.WebsocketInterface.query') as mocked_query:
            mocked_query.return_value = 'value'
            with mock.patch('interfaces.Cache', autospec=True) as mocked_cache:
                mocked_cache.is_cached.return_value = False
                self.web_sock_interface.cache = mocked_cache
                self.web_sock_interface.cached_query('key')
                mocked_cache.store_key_value.assert_called_once_with(
                    'key', 'value')

    def test_cache_query_retrieve_invalid_key_bad_query(self):
        """Tests that the method returns None if key is not in cache and query returns None"""
        with mock.patch('interfaces.WebsocketInterface.query') as mocked_query:
            mocked_query.return_value = None
            result = self.web_sock_interface.cached_query('key', False)
            self.assertEqual(None, result)
