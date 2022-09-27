from settings import cfg, logger
from solana.rpc.api import Client
from helpers import strip_url, url_join, validate_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector
import requests


class solana_collector():

    def __init__(self, rpc_metadata):

        try:
            self.subscribe_url = rpc_metadata['subscribe_url']
        except KeyError:
            logger.error(
                "Please note that solana collector requires subscribe_url websocket endpoint on top of regular url. Please refer to example configuration for example"
            )

        validate_protocol(rpc_metadata['subscribe_url'], 'wss')
        validate_protocol(rpc_metadata['url'], 'https')
        self.url = rpc_metadata['url']
        self.health_uri = url_join(self.url, "/health")
        self.client = Client(self.url, timeout=cfg.response_timeout)

        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        self.ws_collector = websocket_collector(self.subscribe_url,
                                                sub_payload={
                                                    "jsonrpc": "2.0",
                                                    "id": 1,
                                                    "method": "slotSubscribe"
                                                })
        self.ws_collector.setDaemon(True)
        self.ws_collector.start()

    def is_connected(self) -> bool:
        """Health check."""
        try:
            response = requests.get(self.health_uri, timeout=cfg.response_timeout)
            response.raise_for_status()
        except (IOError, requests.HTTPError) as err:
            logger.error("Health check failed for {}: {}".format(strip_url(self.health_uri), err))
            return False
        return response.ok

    def probe(self, metrics):
        try:
            if self.is_connected():
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['brpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['brpc_block_height'].add_metric(self.labels_values, self.client.get_block_height()['result'])
            else:
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
