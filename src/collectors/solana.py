from settings import logger
from helpers import strip_url, generate_labels_from_metadata
import requests
from metrics_processor import results
from time import perf_counter
from collectors.ws import subscription
from collectors.https import https_connection


class solana_collector():

    def __init__(self, rpc_metadata):
        self.url, self.subscribe_url, self.stripped_url = rpc_metadata['url'], rpc_metadata['subscribe_url'], strip_url(
            rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        self.client = https_connection(self.url)

        sub_payload = {"method": "slotSubscribe", "jsonrpc": "2.0", "id": 1}
        self.sub = subscription(self.subscribe_url, sub_payload)
        self.sub.isDaemon()
        self.sub.start()

    def _get_client_version(self):
        payload = {'jsonrpc': '2.0', 'method': "getVersion", 'id': 1}
        response = requests.post(self.url, json=payload).json()['result']['solana-core']
        return response

    def _get_block_height(self):
        payload = {'jsonrpc': '2.0', 'method': "getBlockHeight", 'id': 1}
        response = requests.post(self.url, json=payload).json()
        return response['result']

    def probe(self) -> results:
        results.register(self.url, self.labels_values)
        health_check_payload = {'jsonrpc': '2.0', 'method': "getVersion", 'id': 1}
        try:
            if self.client.is_connected_post_check(health_check_payload):
                results.record_latency(self.url, self.client.get_latency(health_check_payload))
                results.record_health(self.url, True)
                results.record_client_version(self.url, self._get_client_version())
                results.record_block_height(self.url, self._get_block_height())
                results.record_head_count(self.url, self.sub.head_counter)
            else:
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error(f"{exc}", url=self.stripped_url)
            results.record_health(self.url, False)
