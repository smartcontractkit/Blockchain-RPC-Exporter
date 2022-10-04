from settings import logger, cfg
from helpers import strip_url, generate_labels_from_metadata, hex_to_int, key_from_json_str
from metrics_processor import results

from collectors.ws import subscription, fetch_latency
import websockets
import asyncio
import json


class evm_collector():

    def __init__(self, rpc_metadata):
        self.url, self.chain_id, self.stripped_url = rpc_metadata['url'], rpc_metadata['chain_id'], strip_url(
            rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

        sub_payload = {"method": "eth_subscribe", "jsonrpc": "2.0", "id": self.chain_id, "params": ["newHeads"]}
        self.sub = subscription(self.url, sub_payload)
        self.sub.isDaemon()
        self.sub.start()

    async def _web3_clientVersion(self, websocket):
        payload = {"jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": self.chain_id}
        await websocket.send(json.dumps(payload))
        result = await websocket.recv()
        return key_from_json_str(result, "result")

    async def _eth_blockNumber(self, websocket):
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": self.chain_id}
        await websocket.send(json.dumps(payload))
        result = await websocket.recv()
        return hex_to_int(key_from_json_str(result, "result"))

    async def _probe(self) -> results:
        """Registers itself against results class and populates various metrics for prometheus registry to yield."""
        results.register(self.url, self.labels_values)
        try:
            async with websockets.connect(self.url,
                                          open_timeout=cfg.open_timeout,
                                          close_timeout=cfg.close_timeout,
                                          ping_interval=cfg.ping_interval,
                                          ping_timeout=cfg.ping_timeout) as websocket:
                results.record_latency(self.url, await fetch_latency(websocket))
                results.record_health(self.url, True)
                results.record_block_height(self.url, await self._eth_blockNumber(websocket))
                results.record_client_version(self.url, await self._web3_clientVersion(websocket))
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
