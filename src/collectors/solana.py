from settings import cfg, logger
from solana.rpc.api import Client
from helpers import strip_url, url_join
from collectors.ws import websocket_collector
import requests


class solana_collector():

    def __init__(self, ws_url, https_url, provider):
        self.labels = ['ws_url'
                       'https_url', 'provider', 'blockchain', 'network_name', 'network_type']
        self.labels_values = [ws_url, https_url, provider, cfg.blockchain, cfg.network_name, cfg.network_type]
        self.ws_collector = websocket_collector(ws_url,
                                                sub_payload={
                                                    "jsonrpc": "2.0",
                                                    "id": 1,
                                                    "method": "slotSubscribe"
                                                })
        self.ws_collector.setDaemon(True)
        self.ws_collector.start()
        self.client = Client(https_url, timeout=cfg.response_timeout)
        self.health_uri = url_join(https_url, "/health")

    def is_connected(self) -> bool:
        """Health check."""
        try:
            response = requests.get(self.health_uri, timeout=cfg.response_timeout)
            response.raise_for_status()
        except (IOError, requests.HTTPError) as err:
            logger.error("Health check failed for {}.".format(strip_url(self.health_uri)))
            return False
        return response.ok

    def probe(self, metrics):
        try:
            if self.is_connected():
                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['ws_rpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['ws_rpc_block_height'].add_metric(self.labels_values, self.client.get_block_height()['result'])
            else:
                metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
