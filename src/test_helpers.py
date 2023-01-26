"""Test module for helpers"""
# pylint: disable=protected-access
from unittest import TestCase
from structlog.testing import capture_logs

from helpers import strip_url, return_and_validate_rpc_json_result


class TestHelpers(TestCase):
    """Tests all helper functions"""

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
        logger_metadata = {'component': 'helper'}
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_error_log_for_invalid_rpc_json(self):
        """Tests that a KeyError causes an error log"""
        message = '{"key": "valid but not rpc json"}'
        logger_metadata = {'component': 'helper'}
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_error_log_for_rpc_error(self):
        """Tests that if the message has an rpc error we log an error"""
        message = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}'
        logger_metadata = {'component': 'helper'}
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertTrue(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_does_not_log_error_for_valid(self):
        """Tests that for a valid rpc message no errors are logged"""
        message = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
        logger_metadata = {'component': 'helper'}
        with capture_logs() as captured:
            return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertFalse(
            any([log['log_level'] == "error" for log in captured]))

    def test_return_and_validate_rpc_json_result_return_none_for_rpc_error(self):
        """Tests that if the message has an rpc error we return None"""
        message = '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null}'
        logger_metadata = {'component': 'helper'}
        result = return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertEqual(None, result)

    def test_return_and_validate_rpc_json_result_valid(self):
        """Tests that for a valid case the value for the result key is returned"""
        message = '{"jsonrpc": "2.0", "result": -19, "id": 2}'
        logger_metadata = {'component': 'helper'}
        result = return_and_validate_rpc_json_result(message, logger_metadata)
        self.assertEqual(-19, result)
