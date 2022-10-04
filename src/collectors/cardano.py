from settings import logger, cfg
from helpers import strip_url, generate_labels_from_metadata, key_from_json_str
from metrics_processor import results
import json
import websockets
import asyncio
from collectors.ws import fetch_latency


class cardano_collector():

    def __init__(self, rpc_metadata):
        self.url, self.stripped_url = rpc_metadata['url'], strip_url(rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

    async def _blockHeight(self, websocket):
        payload = {
            "type": "jsonwsp/request",
            "version": "1.0",
            "servicename": "ogmios",
            "methodname": "Query",
            "args": {
                "query": "blockHeight"
            }
        }
        await websocket.send(json.dumps(payload))
        result = await asyncio.wait_for(websocket.recv(), timeout=cfg.response_timeout)
        return key_from_json_str(result, "result")

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
                results.record_block_height(self.url, await self._blockHeight(websocket))
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
