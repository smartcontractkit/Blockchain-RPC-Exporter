import asyncio
from bitcoinrpc import BitcoinRPC
from helpers import strip_url, validate_protocol, generate_labels_from_metadata
from time import perf_counter
from settings import logger


class bitcoin_collector():

    def __init__(self, rpc_metadata):
        validate_protocol(rpc_metadata['url'], "https")
        self.url = rpc_metadata['url']
        self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

    async def _probe(self, metrics):
        try:
            async with BitcoinRPC(self.url, "admin", "admin") as rpc:
                start = perf_counter()
                chain_info = await rpc.getblockchaininfo()
                latency = (perf_counter() - start) * 1000

                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_latency'].add_metric(self.labels_values, latency)
                metrics['brpc_block_height'].add_metric(self.labels_values, chain_info['headers'])
                metrics['brpc_total_difficulty'].add_metric(self.labels_values, chain_info['difficulty'])
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)

    def probe(self, metrics):
        asyncio.run(self._probe(metrics))
