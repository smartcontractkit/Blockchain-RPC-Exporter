"""Module for providing useful functions accessible globally."""

import urllib.parse
from log import logger
import requests
import base64
from jsonrpcclient import Ok, parse_json


def strip_url(url) -> str:
    """Returns a stripped url from all parameters, usernames or passwords if present.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname


def return_and_validate_rpc_json_result(message: str, logger_metadata) -> dict:
    """Loads json rpc response text and validates the response
    as per JSON-RPC 2.0 Specification. In case the message is
    not valid it returns None. This method is used by both HTTPS and 
    Websocket Interface."""
    try:
        message = parse_json(message)
        if isinstance(message, Ok):
            return message.result
    except requests.exceptions.JSONDecodeError as error:
        logger.error('Invalid JSON object in RPC message.',
                     base64_encoded_message=base64.b64encode(message),
                     error=error,
                     **logger_metadata)
    logger.error('Error in RPC message.', message=message, **logger_metadata)
    return None
