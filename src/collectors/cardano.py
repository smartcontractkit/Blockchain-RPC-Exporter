from settings import logger
import json
from collectors.ws import websocket_collector
from helpers import check_protocol, strip_url, generate_labels_from_metadata
from metrics_processor import results


class cardano_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "wss") or check_protocol(self.url, "ws"):
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
            self.ws_collector = websocket_collector(self.url)
        else:
            logger.error("Please provide https endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def _get_block_height(self):
        blk_height_payload = {
            "type": "jsonwsp/request",
            "version": "1.0",
            "servicename": "ogmios",
            "methodname": "Query",
            "args": {
                "query": "blockHeight"
            }
        }
        try:
            return json.loads(self.ws_collector.query(blk_height_payload))['result']
        except KeyError as err:
            logger.error("Failed to fetch block height for {}, error: {}".format(strip_url(self.url), err))

    def probe(self):
        results.register(self.url, self.labels_values)
        try:
            alive = self.ws_collector.get_liveliness()
            if alive:
                results.record_health(self.url, True)
                results.record_latency(self.url, self.ws_collector.get_latency())
                results.record_block_height(self.url, self._get_block_height())
            else:
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
