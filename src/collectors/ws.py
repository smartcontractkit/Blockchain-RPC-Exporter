import asyncio
import websockets
import json
from helpers import strip_url
import threading
from time import perf_counter
from settings import logger
from configuration import cfg


class subscription(threading.Thread):

    def __init__(self, url, payload):
        threading.Thread.__init__(self)
        self.url, self.stripped_url = url, strip_url(url)
        self.payload = payload

        self.first_disconnect = False
        self.head_counter = 0
        self.disconnects = 0

    def run(self):
        asyncio.run(self._subscribe())

    async def _message_counter(self, websocket):
        async for _ in websocket:
            self.head_counter += 1

    async def _subscribe(self):
        async for websocket in websockets.connect(self.url,
                                                  open_timeout=cfg.open_timeout,
                                                  close_timeout=cfg.close_timeout,
                                                  ping_interval=cfg.ping_interval,
                                                  ping_timeout=cfg.ping_timeout):
            try:
                # When we establish connection, we arm the first_time boolean, so we can record disconnect if it occurs.
                self.first_disconnect = True
                logger.info("Subscription connection established.", url=self.stripped_url)
                await websocket.send(json.dumps(self.payload))
                await self._message_counter(websocket)
            except websockets.exceptions.ConnectionClosed:
                # Record disconnect only when it occurs for the first time, ignore retry failures.
                if self.first_disconnect:
                    self.disconnects += 1
                self.first_disconnect = False
                logger.error(f"Subscription connection dropped.", url=self.stripped_url)
                continue


async def fetch_latency(websocket):
    start = perf_counter()
    pong = await websocket.ping()
    await asyncio.wait_for(pong, timeout=cfg.response_timeout)
    return (perf_counter() - start) * 1000
