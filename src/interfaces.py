"""Module for providing interface classes for different communication protocols."""
import asyncio
import json
import threading
import base64

from jsonrpcclient import Ok, parse_json
from websockets.client import connect
from websockets.exceptions import ConnectionClosed, WebSocketException
import requests
from urllib3 import Timeout

from helpers import strip_url
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

    def cached_json_rpc_post(self, payload):
        """Calls json_rpc_post and stores the result in in-memory
        cache, by using payload as key.Method will always return
        cached value after the first call. Cache never expires."""
        cache_key = str(payload)
        value = None
        if self.cache.is_cached(cache_key):
            return self.cache.retrieve_key_value(cache_key)

        value = self.json_rpc_post(payload)
        if value is not None:
            self.cache.store_key_value(cache_key, value)

        return value

    def json_rpc_post(self, payload):
        """Sends a post request. It validates http response code, and
        the validity of json-rpc response. If any of the validations
        fail, the method returns type None. """
        response = None
        with self.session as ses:
            try:
                self._logger.debug("Querying endpoint.",
                                   payload=payload,
                                   **self._logger_metadata)
                req = ses.post(self.url,
                               json=payload,
                               timeout=Timeout(connect=self.connect_timeout,
                                               read=self.response_timeout))
                if req.status_code == requests.codes.ok:  #pylint: disable=no-member
                    try:
                        r_j = parse_json(req.text)
                        if isinstance(r_j, Ok):
                            response = r_j.result
                        else:
                            self._logger.error('RPC Response error.',
                                               payload=payload,
                                               response=req.text,
                                               **self._logger_metadata)
                    except requests.exceptions.JSONDecodeError as error:
                        self._logger.error(
                            'Invalid JSON object.',
                            payload=payload,
                            base64_encoded_response=base64.b64encode(req.text),
                            error=error,
                            **self._logger_metadata)
                else:
                    self._logger.error('Bad HTTP response.',
                                       payload=payload,
                                       response_code=req.status_code,
                                       **self._logger_metadata)
            except (IOError, requests.HTTPError) as error:
                self._logger.error("Problem while sending post request.",
                                   payload=payload,
                                   error=error,
                                   **self._logger_metadata)

        return response


class WebsocketSubscription(threading.Thread):
    def __init__(self, url, sub_payload=None, **client_parameters):
        threading.Thread.__init__(self)
        self._url = url
        self._sub_payload = sub_payload
        self._client_parameters = client_parameters

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

class WebsocketInterface(WebsocketSubscription):  #pylint: disable=too-many-instance-attributes
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

    def cached_query(self, payload, skip_checks=False):
        """Calls json_rpc_post and stores the result in in-memory
        cache, by using payload as key.Method will always return
        cached value after the first call. Cache never expires."""

        cache_key = str(payload)
        value = None
        if self.cache.is_cached(cache_key):
            value = self.cache.retrieve_key_value(cache_key)
        else:
            value = asyncio.run(self._query(payload, skip_checks))
            if value is not None:
                self.cache.store_key_value(cache_key, value)
        return value


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
                try:
                    return json.loads(result)['result']
                except (KeyError, json.decoder.JSONDecodeError) as exc:
                    self._logger.error("Failed to decode RPC query response.",
                                       payload=payload,
                                       error=exc,
                                       response=result,
                                       **self._logger_metadata)
                    return None
            else:
                try:
                    response = parse_json(result)
                    if isinstance(response, Ok):
                        return response.result
                    self._logger.error('Error in RPC response.',
                                       payload=payload,
                                       response=result,
                                       **self._logger_metadata)
                    return None
                except requests.exceptions.JSONDecodeError:
                    self._logger.error('Invalid JSON object.',
                                       payload=payload,
                                       **self._logger_metadata)
                    return None
