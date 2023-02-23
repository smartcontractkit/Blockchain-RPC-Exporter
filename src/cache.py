"""Module for providing in-memory cache"""


class Cache():
    """A rudimentary in-memory cache implementation."""

    def __init__(self):
        self._cache = {}

    def is_cached(self, key: str):
        """Check if key is cached."""
        return key in self._cache

    def store_key_value(self, key: str, value):
        """Stores key-value in cache dict."""
        self._cache[key] = value

    def retrieve_key_value(self, key: str):
        """Retrieves key value from cache."""
        return self._cache.get(key)

    def remove_key_from_cache(self, key: str):
        """Deletes a key from cache."""
        return self._cache.pop(key, None)

    def clear_cache(self):
        """Clears the entire cache"""
        self._cache.clear()
