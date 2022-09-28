import asyncio
from bitcoinrpc import BitcoinRPC
from helpers import check_protocol, strip_url, generate_labels_from_metadata
from time import perf_counter
from settings import logger
from metrics_processor import results


class bitcoin_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "https"):
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
        else:
            logger.error("Please provide https endpoint for {}".format(strip_url(self.url)))
            exit(1)

    async def _probe(self) -> results:
        results.register(self.url, self.labels_values)
        try:
            async with BitcoinRPC(self.url, "admin", "admin") as rpc:
                start = perf_counter()
                chain_info = await rpc.getblockchaininfo()
                latency = (perf_counter() - start) * 1000

                
                results.record_health(self.url, True)
                results.record_latency(self.url, latency)
                results.record_block_height(self.url, chain_info['headers'])
                results.record_total_difficulty(self.url, chain_info['difficulty'])
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)

    def probe(self):
        asyncio.run(self._probe())
