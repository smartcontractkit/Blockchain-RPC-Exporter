from helpers import strip_url, check_protocol, generate_labels_from_metadata
from settings import logger
from time import perf_counter
import requests
from metrics_processor import results


class filecoin_collector():

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
            payload = {'jsonrpc': '2.0', 'method': "Filecoin.ChainHead", 'id': 1}
            start = perf_counter()
            response = requests.post(self.url, json=payload)
            latency = (perf_counter() - start) * 1000

            if response.ok:
                results.record_health(self.url, True)
                results.record_latency(self.url, latency)
                results.record_block_height(self.url, response.json()['result']['Height'])
            else:
                logger.error("Bad response from client while fetching Filecoin.ChainHead method for {}: {}".format(
                    strip_url(self.url), response))
                results.record_health(self.url, False)
        except requests.RequestException as exc:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
        except Exception as e:
            logger.error("Health check failed for {}: {}".format(strip_url(self.url), e))
            results.record_health(self.url, False)
