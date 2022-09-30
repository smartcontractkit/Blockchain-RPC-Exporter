from helpers import check_protocol, strip_url, generate_labels_from_metadata
from time import perf_counter
from settings import logger
from metrics_processor import results
import requests


class bitcoin_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "https"):
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        else:
            logger.error("Please provide https endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def probe(self) -> results:
        results.register(self.url, self.labels_values)
        try:
            payload = {"jsonrpc": "1.0", "id": "exporter", "method": "getblockchaininfo", "params": []}
            start = perf_counter()
            response = requests.post(self.url, json=payload).json()
            latency = (perf_counter() - start) * 1000

            if response:
                results.record_health(self.url, True)
                results.record_latency(self.url, latency)
                results.record_block_height(self.url, response['result']['blocks'])
                results.record_total_difficulty(self.url, response['result']['difficulty'])
            else:
                logger.error("Bad response from client {}: {}".format(strip_url(self.url), exc))
                results.record_health(self.url, False)
        except requests.RequestException as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
        except Exception as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
