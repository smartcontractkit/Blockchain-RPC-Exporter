"""Test module for helpers"""
#pylint: disable=protected-access
from unittest import TestCase
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
