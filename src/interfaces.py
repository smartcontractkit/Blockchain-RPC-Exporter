"""Module for providing interface classes for different communication protocols."""
import asyncio
import json
import threading
from time import perf_counter
from datetime import datetime
from websockets.client import connect
from websockets.exceptions import ConnectionClosed, WebSocketException
import requests
from urllib3 import Timeout

from helpers import strip_url, return_and_validate_rpc_json_result, return_and_validate_rest_api_json_result # pylint: disable=line-too-long
from cache import Cache
from log import logger


class HttpsInterface():  # pylint: disable=too-many-instance-attributes
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
        self._latest_query_latency = None

    @property
    def latest_query_latency(self):
        """Returns the last query latency in seconds and resets the value to None"""
        latency = self._latest_query_latency
        self._latest_query_latency = None
        return latency

    def _return_and_validate_request(self, method='GET', payload=None, params=None):
        """Sends a GET or POST request and validates the http response code."""
        with self.session as ses:
            try:
                self._logger.debug(f"Querying endpoint with {method}.",
                                payload=payload,
                                params=params,
                                **self._logger_metadata)
                start_time = perf_counter()
                if method.upper() == 'GET':
                    req = ses.get(self.url,
                                  params=params,
                                  timeout=Timeout(connect=self.connect_timeout,
                                                  read=self.response_timeout))
                elif method.upper() == 'POST':
                    req = ses.post(self.url,
                                   json=payload,
                                   timeout=Timeout(connect=self.connect_timeout,
                                                   read=self.response_timeout))
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                if req.status_code == requests.codes.ok: # pylint: disable=no-member
                    self._latest_query_latency = perf_counter() - start_time
                    return req.text
            except (IOError, requests.HTTPError, json.decoder.JSONDecodeError, ValueError) as error:
                self._logger.error(f"Problem while sending a {method} request.",
                                payload=payload,
                                params=params,
                                error=error,
                                **self._logger_metadata)
            return None

    def json_rpc_post(self, payload):
        """Checks the validity of a successful json-rpc response. If any of the
        validations fail, the method returns type None. """
        response = self._return_and_validate_request(method='POST', payload=payload)
        if response is not None:
            result = return_and_validate_rpc_json_result(
                response, self._logger_metadata)
            if result is not None:
                return result
        return None

    def cached_json_rpc_post(self, payload: dict):
        """Calls json_rpc_post and stores the result in in-memory cache."""
        cache_key = f"rpc:{str(payload)}"

        if self.cache.is_cached(cache_key):
            return_value = self.cache.retrieve_key_value(cache_key)
            return return_value

        value = self.json_rpc_post(payload=payload)
        if value is not None:
            self.cache.store_key_value(cache_key, value)
        return value

    def json_rest_api_get(self, params: dict = None):
        """Checks the validity of a successful json-rpc response. If any of the
        validations fail, the method returns type None. """
        response = self._return_and_validate_request(method='GET', params=params)
        if response is not None:
            result = return_and_validate_rest_api_json_result(
                response, self._logger_metadata)
            if result is not None:
                return result
        return None

    def cached_rest_api_get(self, params: dict = None):
        """Calls json_rest_api_get and stores the result in in-memory cache."""
        cache_key = f"rest:{str(params)}"

        if self.cache.is_cached(cache_key):
            return_value = self.cache.retrieve_key_value(cache_key)
            return return_value

        value = self.json_rest_api_get(params)
        if value is not None:
            self.cache.store_key_value(cache_key, value)
        return value

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
        self.subscription_ping_latency = None
        self.heads_received = 0
        self._latest_message = None
        self.timestamp = datetime.now()

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

    async def _record_latency(self, websocket):
        if (datetime.now() - self.timestamp).total_seconds() > 10:
            self.timestamp = datetime.now()
            self.subscription_ping_latency = websocket.latency

    async def monitor_heads_received(self, websocket):
        """Monitors the heads received (messages) from the websocket.
        If no heads have been received in while the websocket closed
        so a new connection can be created"""
        while True:
            idle_timeout = 60
            prev_heads_received_count = self.heads_received
            await asyncio.sleep(idle_timeout)
            if websocket.closed:
                break
            if prev_heads_received_count == self.heads_received:
                self._logger.error(
                    "Websocket has not received new message within timeout, closing connection...",
                    timeout=idle_timeout,
                    ** self._logger_metadata)
                await websocket.close(code=4000,
                                      reason=f'No new messages within {idle_timeout} seconds')
                break

    async def _process_message(self, websocket):
        asyncio.create_task(
            self.monitor_heads_received(websocket))
        async for msg in websocket:
            await self._record_latency(websocket)
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
        self._latest_query_latency = None

    @property
    def latest_query_latency(self):
        """Returns the last query latency in seconds and resets the value to None"""
        latency = self._latest_query_latency
        self._latest_query_latency = None
        return latency

    def query(self, payload, skip_checks=False):
        """Asyncio handler for _query method."""
        start_time = perf_counter()
        result = asyncio.run(self._query(payload, skip_checks))
        if result is not None:
            self._latest_query_latency = perf_counter() - start_time
        return result

    def cached_query(self, payload, skip_checks=False):
        """Calls json_rpc_post and stores the result in in-memory
        cache, by using payload as key.Method will always return
        cached value after the first call. Cache never expires."""
        cache_key = str(payload)
        if self.cache.is_cached(cache_key):
            value = self.cache.retrieve_key_value(cache_key)
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
