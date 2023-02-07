"""Module for providing interface classes for different communication protocols."""
import asyncio
import json
import threading
import base64

from websockets.client import connect
from websockets.exceptions import ConnectionClosed, WebSocketException
import requests
from urllib3 import Timeout

from helpers import strip_url, return_and_validate_rpc_json_result
from cache import Cache
from log import logger


class HttpsInterface():
    """A https interface, to interact with https RPC endpoints."""

    def __init__(self, url, connect_timeout, response_timeout):
        self.url = url
        self.connect_timeout = connect_timeout
        self.response_timeout = response_timeout
        self.session = requests.Session()
        self._logger = logger
        self._logger_metadata = {
            'component': 'HttpsCollector',
            'url': strip_url(url)
        }
        self.cache = Cache()

    def _return_and_validate_post_request(self, payload: dict) -> str:
        """Sends a POST request and validates the http response code. If
        response code is OK, it returns the response.text, otherwise
        it returns None.
        """
        with self.session as ses:
            try:
                self._logger.debug("Querying endpoint.",
                                   payload=payload,
                                   **self._logger_metadata)
                req = ses.post(self.url,
                               json=payload,
                               timeout=Timeout(connect=self.connect_timeout,
                                               read=self.response_timeout))
                if req.status_code == requests.codes.ok:  # pylint: disable=no-member
                    return req.text
            except (IOError, requests.HTTPError,
                    json.decoder.JSONDecodeError) as error:
                self._logger.error("Problem while sending a post request.",
                                   payload=payload,
                                   error=error,
                                   **self._logger_metadata)
                return None
            return None

    def json_rpc_post(self, payload):
        """Checks the validity of a successful json-rpc response. If any of the
        validations fail, the method returns type None. """
        response = self._return_and_validate_post_request(payload)
        if response is not None:
            result = return_and_validate_rpc_json_result(
                response, self._logger_metadata)
            if result is not None:
                return result
        return None

    def cached_json_rpc_post(self, payload: dict, invalidate_cache=False):
        """Calls json_rpc_post and stores the result in in-memory
        cache, by using payload as key.Method will always return
        cached value after the first call. Cache never expires."""
        cache_key = str(payload)

        if self.cache.is_cached(cache_key):
            return_value = self.cache.retrieve_key_value(cache_key)
            if invalidate_cache:
                self.cache.remove_key_from_cache(cache_key)
            return return_value

        value = self.json_rpc_post(payload)
        if value is not None:
            self.cache.store_key_value(cache_key, value)
        return None


class WebsocketSubscription(threading.Thread):  # pylint: disable=too-many-instance-attributes
    """A thread class used to subscribe and track
    websocket parameters."""

    def __init__(self, url, sub_payload=None, **client_parameters):
        threading.Thread.__init__(self)
        self._url = url
        self._sub_payload = sub_payload
        self._client_parameters = client_parameters

        self._logger = logger
        self._logger_metadata = {
            'component': 'WebsocketSubscription',
            'url': strip_url(url)
        }
        self.healthy = False
        self.disconnects = 0
        self.heads_received = 0
        self._latest_message = None

    def run(self):
        asyncio.run(self._subscribe(self._sub_payload))

    def get_message_property(self, property_name):
        """Every time new websocket message is received it is stored in-memory.
        You can use this function to retrieve information from the latest message.
        """
        if self._latest_message is None:
            self._logger.error(
                "Have not received messages, can't fetch message property.",
                property=property_name,
                **self._logger_metadata)
            return None

        if property_name not in self._latest_message.keys():
            self._logger.error("Failed to fetch requested property.",
                               property=property_name,
                               message=self._latest_message,
                               **self._logger_metadata)
            return None
        return self._latest_message[property_name]

    def get_message_property_to_hex(self, property_name):
        """Calls get_message_property method and attempts to convert the result
        to int. Assumption is that the response is base 16 hexadecimal number."""
        result = self.get_message_property(property_name)
        if result is not None:
            try:
                return int(result, 16)
            except ValueError as error:
                self._logger.error(
                    "Failed to convert block height from hex to int.",
                    error=error,
                    target_number=result,
                    target_type=type(result),
                    **self._logger_metadata)
                return None
        else:
            return None

    async def _process_message(self, websocket):
        async for msg in websocket:
            self.healthy = True
            if msg is not None:
                try:
                    if 'params' in json.loads(msg):
                        msg = json.loads(msg)['params']['result']
                        self._latest_message = msg
                except json.decoder.JSONDecodeError as error:
                    self._logger.error("Failed to decode JSON.",
                                       message=msg,
                                       error=error,
                                       **self._logger_metadata)
                    continue
            self.heads_received += 1

    async def _subscribe(self, payload):
        self._logger.info("Subscribing to endpoint.",
                          payload=payload,
                          **self._logger_metadata)
        async for websocket in connect(self._url, **self._client_parameters):
            try:
                # When we establish connection, we mark the endpoint alive.
                self.healthy = True
                await websocket.send(json.dumps(payload))
                await self._process_message(websocket)
            except ConnectionClosed:
                self._logger.error(
                    "Websocket connection lost, reconnecting...",
                    **self._logger_metadata)
                # We record the disconnect only if it was previously alive.
                if self.healthy:
                    self.disconnects += 1
                self.healthy = False
                continue


class WebsocketInterface(WebsocketSubscription):  # pylint: disable=too-many-instance-attributes
    """A websocket interface, to interact with websocket RPC endpoints."""

    def __init__(self, url, sub_payload=None, **client_parameters):
        super().__init__(url, sub_payload, **client_parameters)
        self._url = url
        self._client_parameters = client_parameters
        self._logger = logger
        self._logger_metadata = {
            'component': 'WebsocketInterface',
            'url': strip_url(url)
        }
        self.cache = Cache()

    def query(self, payload, skip_checks=False):
        """Asyncio handler for _query method."""
        return asyncio.run(self._query(payload, skip_checks))

    def cached_query(self, payload, skip_checks=False, invalidate_cache=False):
        """Calls json_rpc_post and stores the result in in-memory
        cache, by using payload as key.Method will always return
        cached value after the first call. Cache never expires."""
        cache_key = str(payload)
        if self.cache.is_cached(cache_key):
            value = self.cache.retrieve_key_value(cache_key)
            if invalidate_cache:
                self.cache.remove_key_from_cache(cache_key)
            return value

        value = self.query(payload, skip_checks)
        if value is not None:
            self.cache.store_key_value(cache_key, value)
        return value

    def _load_and_validate_json_key(self, message, key):
        try:
            return json.loads(message)[key]
        except (KeyError, json.decoder.JSONDecodeError) as exc:
            self._logger.error("Failed to load key from json.",
                               error=exc,
                               message=message,
                               key=key,
                               **self._logger_metadata)
            return None

    async def _query(self, payload, skip_checks):
        async with connect(self._url, **self._client_parameters) as websocket:
            try:
                self._logger.debug("Querying endpoint.",
                                   payload=payload,
                                   **self._logger_metadata)
                await asyncio.wait_for(
                    websocket.send(json.dumps(payload)),
                    timeout=self._client_parameters['ping_timeout'])
                result = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=self._client_parameters['ping_timeout'])
            except (asyncio.exceptions.TimeoutError,
                    WebSocketException) as exc:
                self._logger.error("JSON RPC Query failed.",
                                   payload=payload,
                                   error=exc,
                                   **self._logger_metadata)
                return None

        if skip_checks:
            return self._load_and_validate_json_key(result, 'result')

        return return_and_validate_rpc_json_result(result,
                                                   self._logger_metadata)
