#pylint: disable=protected-access,invalid-name,line-too-long
"""Module for testing interfaces"""

from unittest import TestCase
import requests
import requests_mock

from interfaces import HttpsInterface
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
