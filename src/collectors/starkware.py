from settings import logger
from helpers import strip_url, check_protocol, generate_labels_from_metadata
from time import perf_counter
import requests


class starkware_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "https"):
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        else:
            logger.error("Please provide https endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def probe(self, metrics):
        try:
            payload = {"method": "starknet_blockNumber", "jsonrpc": "2.0", "id": 1}
            start = perf_counter()

            response = requests.post(self.url, json=payload).json()
            latency = (perf_counter() - start) * 1000

            if response:
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_latency'].add_metric(self.labels_values, latency)
                metrics['brpc_block_height'].add_metric(self.labels_values, response['result'])
            else:
                logger.error("Bad response from client {}: {}".format(strip_url(self.url), exc))
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except requests.RequestException as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
