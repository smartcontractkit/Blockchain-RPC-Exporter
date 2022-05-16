import asyncio
import json
from time import perf_counter
import websockets
import socket
import logging
import urllib.parse
import threading
import settings

LOGLEVEL = settings.LOGLEVEL
logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(message)s')


class rpc_probe(threading.Thread):

    def __init__(self, uris: list, chain_id: int, timeout: int):
        threading.Thread.__init__(self)
        self.uris = uris
        self.timeout = timeout
        self.chain_id = chain_id
        self.results = []
        self.disconnects_counter = self._instantiate_counter()
        self.head_counter = self._instantiate_counter()

    def _instantiate_counter(self):
        dict = {}
        for item in self.uris:
            dict.update({item['url']: 0})
        return dict

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        group = asyncio.gather(*[
            self._listen_forever(rpc['url'], self.chain_id)
            for rpc in self.uris
        ])
        loop.run_until_complete(group)

    async def _message_handler(self, websocket, uri):
        async for message in websocket:
            self.head_counter[uri] += 1

    async def _listen_forever(self, uri, chain_id):
        async for websocket in websockets.connect(uri):
            try:
                await websocket.send(
                    json.dumps({
                        "method": "eth_subscribe",
                        "jsonrpc": "2.0",
                        "id": chain_id,
                        "params": ["newHeads"]
                    }))
                await self._message_handler(websocket, uri)
            except websockets.ConnectionClosed:
                self.disconnects_counter[uri] += 1
                continue

    def get_results(self):
        logging.debug("Results: {}".format(self.results))
        self.results.clear()

        self._collect_handler()
        return self.results

    def _collect_handler(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        group = asyncio.gather(
            *[self._collect(rpc['url'], rpc['provider']) for rpc in self.uris])
        loop.run_until_complete(group)
        loop.close()

    def _set_healthy(self,
                     up,
                     uri,
                     provider,
                     latency=0.0,
                     block_height=0,
                     total_difficulty=0):
        self.results.append({
            "up": up,
            "url": uri,
            "latency": latency,
            "block_height": block_height,
            "total_difficulty": total_difficulty,
            "provider": provider
        })

    async def _fetch_total_difficulty(self, ws, block_height):
        total_difficulty = None
        error = None

        hex_block_number = hex(block_height)
        await asyncio.wait_for(ws.send(
            json.dumps({
                "method": "eth_getBlockByNumber",
                "jsonrpc": "2.0",
                "id": self.chain_id,
                "params": [hex_block_number, False]
            })),
                               timeout=self.timeout)
        response = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
        response_json = json.loads(response)
        if response_json['result'] == None:
            error = "RPC returned response of type `None`"
        else:
            try:
                result = response_json['result']
            except KeyError:
                logging.debug(response_json)
                error = "Key `result` was not found in response while requesting eth_getBlockByNumber"

            if "totalDifficulty" in response_json['result']:
                total_difficulty = int(result['totalDifficulty'], 16)

            elif "error" in response_json:
                error = response_json['error']['message']
            else:
                # Set totalDifficulty to 0 if blockchain does not use it.
                total_difficulty = 0

        return total_difficulty, error

    async def _fetch_block_height(self, ws):
        block_height = None
        error = None

        await asyncio.wait_for(ws.send(
            json.dumps({
                "method": "eth_blockNumber",
                "jsonrpc": "2.0",
                "id": self.chain_id
            })),
                               timeout=self.timeout)
        # TODO: Implement error handling for JSON-RPC 2.0 Specification https://www.jsonrpc.org/specification#error_object
        response = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
        response_json = json.loads(response)
        if response_json['result'] == None:
            error = "RPC returned response of type `None`"
        else:
            result = json.loads(response)
            if "error" in result:
                error = result['error']['message']
            else:
                try:
                    block_height = int(result['result'], 16)
                except KeyError:
                    logging.debug(response)
                    error = "Key `result` was not found in response while requesting eth_blockNumber"
        return block_height, error

    async def _collect(self, uri, provider):
        try:
            async with websockets.connect(uri,
                                          open_timeout=self.timeout,
                                          close_timeout=self.timeout) as ws:
                try:
                    obs_latency_seconds = await self._fetch_latency(ws)
                    obs_block_height, error = await self._fetch_block_height(ws
                                                                             )
                    if error == None:
                        obs_total_difficulty, error = await self._fetch_total_difficulty(
                            ws, obs_block_height)
                        if error == None:
                            self._set_healthy(True, uri, provider,
                                              obs_latency_seconds,
                                              obs_block_height,
                                              obs_total_difficulty)
                        else:
                            self._set_healthy(False, uri, provider,
                                              obs_latency_seconds,
                                              obs_block_height)
                            logging.info('Host: {}, Error: {}'.format(
                                self._get_host_from_uri(uri), error))
                    else:
                        self._set_healthy(False, uri, provider,
                                          obs_latency_seconds)
                        logging.info('Host: {}, Error: {}'.format(
                            self._get_host_from_uri(uri), error))

                    await ws.close()
                except (websockets.exceptions.ConnectionClosed) as error:
                    logging.error('Host: {}, Error: {}'.format(
                        self._get_host_from_uri(uri), error))
                    self._set_healthy(False, uri, provider)
        except (socket.gaierror, ConnectionRefusedError,
                websockets.exceptions.WebSocketException) as error:
            logging.error('Host: {}, Error: {}'.format(
                self._get_host_from_uri(uri), error))
            self._set_healthy(False, uri, provider)

        except asyncio.exceptions.TimeoutError:
            logging.error('Host: {}, connection timed out.'.format(
                self._get_host_from_uri(uri)))
            self._set_healthy(False, uri, provider)

    def _get_host_from_uri(self, uri):
        return urllib.parse.urlparse(uri).netloc

    async def _fetch_latency(self, ws):
        start = perf_counter()
        pong = await ws.ping()
        await asyncio.wait_for(pong, timeout=self.timeout)
        result = (perf_counter() - start)
        result_miliseconds = result * 1000
        return result_miliseconds
