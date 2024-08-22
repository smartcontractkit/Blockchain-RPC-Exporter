"""Module for providing useful functions accessible globally."""

import urllib.parse
import json
from json.decoder import JSONDecodeError
from jsonrpcclient import Ok, parse_json
from log import logger


def strip_url(url) -> str:
    """Returns a stripped url from all parameters, usernames or passwords if present.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname


def return_and_validate_json_result(message: str, type: str,logger_metadata) -> dict:
    """Loads json rpc response text and validates the response
    as per JSON-RPC 2.0 Specification. In case the message is
    not valid it returns None. This method is used by both HTTPS and
    Websocket Interface."""
    try:
        if type=='RPC':
            parsed = parse_json(message)
            if isinstance(parsed, Ok):  # pylint: disable=no-else-return
                return parsed.result
            else:
                logger.error('Error in RPC message.',
                            message=message, **logger_metadata)
        else:
            parsed = json.loads(message)
            return parsed
    except (JSONDecodeError, KeyError) as error:
        logger.error('Invalid JSON RPC object in RPC message.',
                     message=message,
                     error=error,
                     **logger_metadata)

    except Exception as error:
        logger.error('Unexpected error while parsing JSON.',
                     message=message,
                     error=error,
                     **logger_metadata)
    return None

def return_and_validate_rpc_json_result(message: str, logger_metadata) -> dict:
    return return_and_validate_json_result(message,type='RPC',logger_metadata=logger_metadata)

def return_and_validate_restApi_json_result(message: str, logger_metadata) -> dict:
    return return_and_validate_json_result(message,type='REST',logger_metadata=logger_metadata)

def validate_dict_and_return_key_value(data, key, logger_metadata, stringify=False, to_number=False):
    """Validates that a dict is provided and returns the key value either in
    original form or as a string"""
    if isinstance(data, dict):
        value = data.get(key)
        if value is not None:
            if stringify:
                return str(value)
            elif to_number:
                try:
                    return float(value)
                except ValueError:
                    return None
            return value
    logger.error("Provided data is not a dict or has no value for key",
                 key=key,
                 **logger_metadata)
    return None
