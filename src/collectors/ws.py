import threading
import asyncio
import json
import websockets
from settings import logger, cfg
from time import perf_counter
from helpers import strip_url


class websocket_collector(threading.Thread):

    def __init__(self, url, sub_payload=None):
        threading.Thread.__init__(self)
        self.url = url
        self.sub_payload = sub_payload
        self.message_counter = 0
        self.disconnects_counter = 0
        self.first_time = False

    def _get_client(self):
        return websockets.connect(self.url,
                                  logger=logger,
                                  open_timeout=cfg.open_timeout,
                                  ping_interval=cfg.ping_interval,
                                  ping_timeout=cfg.ping_timeout,
                                  close_timeout=cfg.close_timeout)

    def run(self):
        """This method is a threaded method that runs in background. It invokes _subscribe() async method."""
        loop = asyncio.new_event_loop()
        group = asyncio.gather(self._subscribe(self.sub_payload), return_exceptions=True, loop=loop)
        loop.run_until_complete(group)

    def query(self, payload):
        """Query method is used for short lived connections. It is a handler for _query()"""
        loop = asyncio.new_event_loop()
        future = loop.create_task(self._async_query(payload))
        response = loop.run_until_complete(future)
        loop.close()
        return response

    def get_liveliness(self):
        loop = asyncio.new_event_loop()
        future = loop.create_task(self._liveliness_check())
        response = loop.run_until_complete(future)
        loop.close()
        return response

    def get_latency(self):
        loop = asyncio.new_event_loop()
        future = loop.create_task(self._get_latency())
        response = loop.run_until_complete(future)
        loop.close()
        return response

    async def _liveliness_check(self):
        try:
            async with self._get_client() as websocket:
                logger.debug("Recording liveliness for {}".format(strip_url(self.url)))
                pong = await websocket.ping()
                await asyncio.wait_for(pong, timeout=cfg.ping_timeout)
                return True
        except Exception as exc:
            logger.error("Failed liveness check {}:{} for {}".format(type(exc), exc, strip_url(self.url)))
            return False

    async def _get_latency(self):
        try:
            async with self._get_client() as websocket:
                logger.debug("Recording latency for {}".format(strip_url(self.url)))
                start = perf_counter()
                pong = await websocket.ping()
                await asyncio.wait_for(pong, timeout=cfg.ping_timeout)
                return (perf_counter() - start) * 1000
        except Exception as exc:
            logger.error("Failed latency fetch {}:{} for {}".format(type(exc), exc, strip_url(self.url)))

    async def _async_query(self, payload):
        """Opens a connection, sends a query and returns a RPC response."""
        try:
            client = self._get_client()
            async with client as websocket:
                await websocket.send(json.dumps(payload))
                return await websocket.recv()
        except Exception as exc:
            logger.error("Failed query {}:{} for {}".format(type(exc), exc, strip_url(self.url)))

    async def _subscribe(self, payload):
        async for websocket in self._get_client():
            try:
                # When we establish connection, we arm the first_time boolean, so we can record disconnect if it occurs.
                self.first_time = True
                await websocket.send(json.dumps(payload))
                await self._message_counter(websocket)
            except websockets.exceptions.ConnectionClosed:
                # Record disconnect only when it occurs for the first time, ignore retry failures.
                if self.first_time:
                    self.disconnects += 1
                self.first_time = False
                logger.error("Connection dropped {}".format(strip_url(self.websocket_url)))
                continue

    async def _message_counter(self, websocket):
        async for _ in websocket:
            self.message_counter += 1
