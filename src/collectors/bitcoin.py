from helpers import strip_url, generate_labels_from_metadata
from settings import logger
from metrics_processor import results
import requests
from collectors.https import https_connection


class bitcoin_collector():

    def __init__(self, rpc_metadata):
        self.url, self.stripped_url = rpc_metadata['url'], strip_url(rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        self.client = https_connection(self.url)

    def _get_client_version(self):
        payload = {"jsonrpc": "1.0", "id": "exporter", "method": "getnetworkinfo", "params": []}
        response = requests.post(self.url, json=payload).json()['result']
        version, subversion, protocolversion = response['version'], response['subversion'], response['protocolversion']
        version = f"version:{version} subversion:{subversion} protocolversion:{protocolversion}"
        return version

    def _get_height_and_difficulty(self):
        payload = {"jsonrpc": "1.0", "id": "exporter", "method": "getblockchaininfo", "params": []}
        response = requests.post(self.url, json=payload).json()
        block_height = response['result']['blocks']
        total_difficulty = response['result']['difficulty']
        return block_height, total_difficulty

    def probe(self) -> results:
        results.register(self.url, self.labels_values)
        health_check_payload = {"jsonrpc": "1.0", "id": "exporter", "method": "getnetworkinfo"}
        try:
            if self.client.is_connected_post_check(health_check_payload):
                results.record_latency(self.url, self.client.get_latency(health_check_payload))
                results.record_health(self.url, True)

                block_height, total_difficulty = self._get_height_and_difficulty()
                results.record_client_version(self.url, self._get_client_version())
                results.record_block_height(self.url, block_height)
                results.record_total_difficulty(self.url, total_difficulty)
            else:
                logger.error("The url did not pass liveness check.", self.stripped_url)
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error(f"{exc}", url=self.stripped_url)
            results.record_health(self.url, False)
