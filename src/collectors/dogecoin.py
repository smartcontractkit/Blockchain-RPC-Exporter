from helpers import strip_url
from settings import cfg, logger
from time import perf_counter
import requests


class doge_collector():

    def __init__(self, https_url, provider):
        self.https_url = https_url
        self.labels = [
            'https_url', 'provider', 'blockchain', 'network_name',
            'network_type'
        ]
        self.labels_values = [
            https_url, provider, cfg.blockchain, cfg.network_name,
            cfg.network_type
        ]

    def probe(self, metrics):
        try:
            payload = {'version': '1.1', 'method': "getinfo", 'id': 1}
            start = perf_counter()
            response = requests.post(self.https_url, json=payload).json()
            latency = (perf_counter() - start) * 1000

            if response:
                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_latency'].add_metric(self.labels_values,
                                                     latency)
                metrics['ws_rpc_block_height'].add_metric(
                    self.labels_values, response['result']['blocks'])
                metrics['ws_rpc_total_difficulty'].add_metric(
                    self.labels_values, response['result']['difficulty'])
            else:
                logger.error("Bad response from client {}: {}".format(
                    strip_url(self.https_url), exc))
                metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except requests.RequestException as exc:
            logger.error("Health check failed for {}: {}".format(
                strip_url(self.https_url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except Exception as e:
            logger.error("Health check failed for {}: {}".format(
                strip_url(self.https_url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
