from settings import cfg, logger
from solana.rpc.api import Client
from helpers import strip_url, url_join, check_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector
import requests
from metrics_processor import results

class solana_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "https"):
            self.health_uri = url_join(self.url, "/health")
            self.client = Client(self.url, timeout=cfg.response_timeout)

            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        else:
            logger.error("Please provide https endpoint for {}".format(strip_url(self.url)))
            exit(1)

        try:
            self.subscribe_url = rpc_metadata['subscribe_url']
        except KeyError:
            logger.error(
                "Please note that solana collector requires subscribe_url websocket endpoint on top of regular url. Please refer to example configuration for example"
            )

        if check_protocol(self.subscribe_url, "wss") or check_protocol(self.subscribe_url, 'ws'):
            self.ws_collector = websocket_collector(self.subscribe_url,
                                                    sub_payload={
                                                        "jsonrpc": "2.0",
                                                        "id": 1,
                                                        "method": "slotSubscribe"
                                                    })
            self.ws_collector.setDaemon(True)
            self.ws_collector.start()
        else:
            logger.error("Please provide wss/ws endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def is_connected(self) -> bool:
        """Health check."""
        try:
            response = requests.get(self.health_uri, timeout=cfg.response_timeout)
            response.raise_for_status()
        except (IOError, requests.HTTPError) as err:
            logger.error("Health check failed for {}: {}".format(strip_url(self.health_uri), err))
            return False
        return response.ok

    def probe(self) -> results:
        results.register(self.url, self.labels_values)
        try:
            if self.is_connected():
                results.record_health(self.url, True)
                results.record_head_count(self.url, self.ws_collector.message_counter)
                results.record_disconnects(self.url, self.ws_collector.disconnects_counter)
                results.record_block_height(self.url, self.client.get_block_height()['result'])
            else:
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
