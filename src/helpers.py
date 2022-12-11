"""Module for providing useful functions accessible globally."""

import urllib.parse


def strip_url(url) -> str:
    """Returns a stripped url from all parameters, usernames or passwords if present.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname
