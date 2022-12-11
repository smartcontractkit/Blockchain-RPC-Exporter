 #pylint: disable=protected-access, import-error
"""Test module for Cache"""
import unittest
from src.cache import Cache


class TestCache(unittest.TestCase):
    """Tests all cache functionalities"""

    def setUp(self):
        """Loads cache."""
        self.cache = Cache() #

    def test_cache_type_attribute(self):
        """Check if cache is empty after instantiation."""
        self.assertTrue(self.cache._cache == {})

    def test_store_key_value(self):
        """Check if storing a value in cache works."""
        self.cache.store_key_value("key", "value")
        self.assertEqual(self.cache._cache, {"key": "value"})

    def test_retrieve_key_value(self):
        """Check if retrieve key value from cache works."""
        self.cache.store_key_value("key", "value")
        self.assertEqual(self.cache.retrieve_key_value("key"), "value")
        self.assertEqual(self.cache.retrieve_key_value("wrongkey"), None)

    def test_remove_key_from_cache(self):
        """ Check if removing cache key works as expected."""
        self.cache.store_key_value("key", "value")
        self.assertEqual(self.cache._cache, {"key": "value"})
        self.cache.remove_key_from_cache("key")
        self.assertEqual(self.cache._cache, {})

    def test_is_cached(self):
        """Check cache checker method."""
        self.cache.store_key_value("key", "value")
        self.assertTrue(self.cache.is_cached("key"))
        self.assertFalse(self.cache.is_cached("wrongkey"))
