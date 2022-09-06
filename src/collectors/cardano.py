from settings import cfg, logger
import json
from collectors.ws import websocket_collector
from helpers import strip_url


class cardano_collector():

    def __init__(self, url, provider):
        self.labels = ['url', 'provider', 'blockchain', 'network_name', 'network_type', 'evmChainID']
        self.labels_values = [url, provider, cfg.blockchain, cfg.network_name, cfg.network_type]
        self.url = url
        self.ws_collector = websocket_collector(url, provider)

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
                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['ws_rpc_block_height'].add_metric(self.labels_values, self._get_block_height())
            else:
                metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
