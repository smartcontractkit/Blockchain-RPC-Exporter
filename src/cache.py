"""Module for providing in-memory cache"""


class Cache():
    """A rudimentary in-memory cache implementation."""

    def __init__(self):
        self._cache = {}

    def is_cached(self, key: str):
        """Check if key is cached."""
        if key in self._cache:
            return True
        return False

    def store_key_value(self, key: str, value):
        """Stores key-value in cache dict."""
        self._cache[key] = value

    def retrieve_key_value(self, key: str):
        """Retrieves key value from cache."""
        if self.is_cached(key):
            return self._cache.get(key)
        return None

    def remove_key_from_cache(self, key: str):
        """Deletes a key from cache."""
        if self.is_cached(key):
            del self._cache[key]

    def clear_cache(self):
        """Clears the entire cache"""
        self._cache.clear()
