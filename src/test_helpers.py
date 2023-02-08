"""Test module for helpers"""
# pylint: disable=protected-access
from unittest import TestCase
from structlog.testing import capture_logs

from helpers import strip_url, return_and_validate_rpc_json_result, validate_dict_and_return_key_value


class TestHelpers(TestCase):
    """Tests all helper functions"""

    def setUp(self):
        self.collector_logger_metadata = {
            'component': 'Collector',
            'url': 'test.com'
        }
        self.logger_metadata = {'component': 'helper'}

    def test_strip_url_wss(self):
        """Tests stripping url for websocket endpoints."""
        url = 'wss://testendpoint1.com/ws/?apikey=123456'
        self.assertEqual(strip_url(url), "testendpoint1.com")

    def test_strip_url_https(self):
        """Tests stripping url for https endpoints."""
        url = 'https://testendpoint2.com?auth=123456'
        self.assertEqual(strip_url(url), "testendpoint2.com")

    def test_return_and_validate_rpc_json_result_error_log_for_invalid_json(self):
        """Tests that a JSONDecodeError causes an error log"""
        message = '{"key": invalid}'
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, self.logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_error_log_for_invalid_rpc_json(self):
        """Tests that a KeyError causes an error log"""
        message = '{"key": "valid but not rpc json"}'
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, self.logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_error_log_for_rpc_error(self):
        """Tests that if the message has an rpc error we log an error"""
        message = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}'
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, self.logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_does_not_log_error_for_valid(self):
        """Tests that for a valid rpc message no errors are logged"""
        message = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, self.logger_metadata)
        self.assertFalse(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_return_none_for_rpc_error(self):
        """Tests that if the message has an rpc error we return None"""
        message = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}'
        result = return_and_validate_rpc_json_result(
            message, self.logger_metadata)
        self.assertEqual(None, result)

    def test_return_and_validate_rpc_json_result_valid(self):
        """Tests that for a valid case the value for the result key is returned"""
        message = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
        result = return_and_validate_rpc_json_result(
            message, self.logger_metadata)
        self.assertEqual(-19, result)

    def test_validate_dict_and_return_key_value_no_dict_returns_none(self):
        """Tests that if provided with a non dict type None is returned"""
        dictionary = "This is not a dict type"
        result = validate_dict_and_return_key_value(
            dictionary, 'key', self.collector_logger_metadata)
        self.assertEqual(None, result)

    def test_validate_dict_and_return_key_value_with_valid_dict(self):
        """Tests that if provided with a valid dict the value of key is returned"""
        dictionary = {"key": -19}
        result = validate_dict_and_return_key_value(
            dictionary, 'key', self.collector_logger_metadata)
        self.assertEqual(-19, result)

    def test_validate_dict_and_return_key_value_with_invalid_key(self):
        """Tests that if provided with a invalid key None is returned"""
        dictionary = {"bad": "key"}
        result = validate_dict_and_return_key_value(
            dictionary, 'key', self.collector_logger_metadata)
        self.assertEqual(None, result)

    def test_validate_dict_and_return_key_value_with_valid_dict_stringify(self):
        """Tests that if provided with a valid dict the value of key is returned as a string"""
        dictionary = {"key": -19}
        result = validate_dict_and_return_key_value(
            dictionary, 'key', self.collector_logger_metadata, stringify=True)
        self.assertEqual("-19", result)

    def test_validate_dict_and_return_key_value_error_log(self):
        """Tests that an error is logged when no valid key is found"""
        dictionary = {"key": -19}
        with capture_logs() as captured:
            validate_dict_and_return_key_value(
                dictionary, 'wrongkey', self.collector_logger_metadata, stringify=True)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_validate_dict_and_return_key_value_no_error_log(self):
        """Tests that no error is logged when a valid key value is found"""
        dictionary = {"key": -19}
        with capture_logs() as captured:
            validate_dict_and_return_key_value(
                dictionary, 'key', self.collector_logger_metadata, stringify=True)
        self.assertFalse(
            any([log['log_level'] == "error" for log in captured]))
