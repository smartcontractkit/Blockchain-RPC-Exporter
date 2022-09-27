from helpers import strip_url, validate_protocol, generate_labels_from_metadata
from settings import logger
from time import perf_counter
import requests


class doge_collector():

    def __init__(self, rpc_metadata):
        validate_protocol(rpc_metadata['url'], "https")
        self.url = rpc_metadata['url']
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

    def probe(self, metrics):
        try:
            payload = {'version': '1.1', 'method': "getinfo", 'id': 1}
            start = perf_counter()
            response = requests.post(self.url, json=payload).json()
            latency = (perf_counter() - start) * 1000

            if response:
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_latency'].add_metric(self.labels_values, latency)
                metrics['brpc_block_height'].add_metric(self.labels_values, response['result']['blocks'])
                metrics['brpc_total_difficulty'].add_metric(self.labels_values, response['result']['difficulty'])
            else:
                logger.error("Bad response from client {}: {}".format(strip_url(self.url), exc))
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except requests.RequestException as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
