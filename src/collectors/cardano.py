from settings import logger
import json
from collectors.ws import websocket_collector
from helpers import check_protocol, strip_url, generate_labels_from_metadata


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

    def probe(self, metrics):
        try:
            alive = self.ws_collector.get_liveliness()
            if alive:
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['brpc_block_height'].add_metric(self.labels_values, self._get_block_height())
            else:
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
