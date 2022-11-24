from helpers import strip_url, generate_labels_from_metadata
from settings import logger
import requests
from metrics_processor import results
from collectors.https import https_connection


class filecoin_collector():

    def __init__(self, rpc_metadata):
        self.url, self.stripped_url = rpc_metadata['url'], strip_url(rpc_metadata['url'])
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        self.client = https_connection(self.url)

    def _get_client_version(self):
        payload = {'jsonrpc': '2.0', 'method': "Filecoin.Version", 'id': 1}
        response = requests.post(self.url, json=payload).json()['result']
        version, apiVersion, = response['Version'], response['APIVersion']
        version = f"Version:{version} APIVersion:{apiVersion}"
        return version

    def _get_block_height(self):
        payload = {'jsonrpc': '2.0', 'method': "Filecoin.ChainHead", 'id': 1}
        response = requests.post(self.url, json=payload).json()
        return response['result']['Height']

    def probe(self) -> results:
        health_check_payload = {'jsonrpc': '2.0', 'method': "Filecoin.Version", 'id': 1}
        results.register(self.url, self.labels_values)
        try:
            if self.client.is_connected_post_check(health_check_payload):
                results.record_latency(self.url, self.client.get_latency(health_check_payload))
                results.record_health(self.url, True)
                results.record_client_version(self.url, self._get_client_version())
                results.record_block_height(self.url, self._get_block_height())
            else:
                results.record_health(self.url, False)
        except Exception as exc:
            logger.error(f"{exc}", url=self.stripped_url)
            results.record_health(self.url, False)
