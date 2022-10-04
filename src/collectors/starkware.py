from settings import logger
from helpers import strip_url, generate_labels_from_metadata
import requests
from metrics_processor import results
from collectors.https import https_connection


class starkware_collector():

    def __init__(self, rpc_metadata):
        self.url, self.stripped_url = rpc_metadata['url'], strip_url(rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        self.client = https_connection(self.url)

    def _blockNumber(self):
        payload = {"method": "starknet_blockNumber", "jsonrpc": "2.0", "id": 1}
        response = requests.post(self.url, json=payload).json()['result']
        return response

    def probe(self) -> results:
        results.register(self.url, self.labels_values)
        health_check_payload = {"method": "starknet_chainId", "jsonrpc": "2.0", "id": 1}
        try:
            if self.client.is_connected_post_check(health_check_payload):
                results.record_latency(self.url, self.client.get_latency(health_check_payload))
                results.record_health(self.url, True)
                results.record_block_height(self.url, self._blockNumber())
            else:
                logger.error(f"Url did not pass liveness check.", url=self.stripped_url)
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error(f"{exc}", url=self.stripped_url)
            results.record_health(self.url, False)
