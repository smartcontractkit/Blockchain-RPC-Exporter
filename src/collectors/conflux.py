from settings import logger
from cfg import cfg
from helpers import strip_url, generate_labels_from_metadata, hex_to_int, key_from_json_str
from metrics_processor import results

from collectors.ws import subscription, fetch_latency
import websockets
import asyncio
import json


class conflux_collector():

    def __init__(self, rpc_metadata):
        self.url, self.chain_id, self.stripped_url = rpc_metadata['url'], rpc_metadata['chain_id'], strip_url(
            rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

        sub_payload = {"method": "cfx_subscribe", "jsonrpc": "2.0", "id": 1, "params": ["newHeads"]}
        self.sub = subscription(self.url, sub_payload)
        self.sub.isDaemon()
        self.sub.start()

    async def _cfx_clientVersion(self, websocket):
        payload = {"jsonrpc": "2.0", "method": "cfx_clientVersion", "params": [], "id": 1}
        await websocket.send(json.dumps(payload))
        result = await asyncio.wait_for(websocket.recv(), timeout=cfg.response_timeout)
        return key_from_json_str(result, "result")

    async def _cfx_epochNumber(self, websocket):
        payload = {"jsonrpc": "2.0", "method": "cfx_epochNumber", "params": [], "id": 1}
        await websocket.send(json.dumps(payload))
        result = await asyncio.wait_for(websocket.recv(), timeout=cfg.response_timeout)
        return hex_to_int(key_from_json_str(result, "result"))

    async def _probe(self) -> results:
        results.register(self.url, self.labels_values)
        try:
            async with websockets.connect(self.url,
                                          open_timeout=cfg.open_timeout,
                                          close_timeout=cfg.close_timeout,
                                          ping_interval=cfg.ping_interval,
                                          ping_timeout=cfg.ping_timeout) as websocket:
                results.record_latency(self.url, await fetch_latency(websocket))
                results.record_health(self.url, True)
                results.record_block_height(self.url, await self._cfx_epochNumber(websocket))
                results.record_client_version(self.url, await self._cfx_clientVersion(websocket))
                results.record_head_count(self.url, self.sub.head_counter)
                results.record_disconnects(self.url, self.sub.disconnects)
        except asyncio.exceptions.TimeoutError:
            logger.error(
                f"Timed out while trying to establish websocket connection. Current open_timeout value in config: {cfg.open_timeout}.",
                url=self.stripped_url)
            results.record_health(self.url, False)
        except Exception as exc:
            results.record_health(self.url, False)
            logger.error(f"{exc}", url=self.stripped_url)

    def probe(self):
        asyncio.run(self._probe())
