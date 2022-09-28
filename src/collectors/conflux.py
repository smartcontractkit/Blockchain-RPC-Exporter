from settings import cfg, logger
from conflux_web3 import Web3
import asyncio
from helpers import strip_url, check_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector
from metrics_processor import results


class conflux_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(self.url, "wss") or check_protocol(self.url, 'ws'):
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)
            self.client = Web3(Web3.WebsocketProvider(self.url, websocket_timeout=cfg.response_timeout))
            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

            self.ws_collector = websocket_collector(self.url,
                                                    sub_payload={
                                                        "method": "cfx_subscribe",
                                                        "jsonrpc": "2.0",
                                                        "id": 1,
                                                        "params": ["newHeads"]
                                                    })
            self.ws_collector.setDaemon(True)
            self.ws_collector.start()
        else:
            logger.error("Please provide wss/ws endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def probe(self):
        results.register(self.url, self.labels_values)
        try:
            if self.client.isConnected():
                results.record_health(self.url, True)
                results.record_head_count(self.url, self.ws_collector.message_counter)
                results.record_disconnects(self.url, self.ws_collector.disconnects_counter)
                results.record_latency(self.url, self.ws_collector.get_latency())
                results.record_block_height(self.url, self.client.cfx.epoch_number)
                try:
                    difficulty = self.client.cfx.get_block_by_hash(self.client.cfx.get_best_block_hash())['difficulty']
                    results.record_difficulty(self.url, difficulty)
                except TypeError:
                    logger.error(
                        "RPC Endpoint sent faulty response type when querying for difficulty. This is most likely issue with RPC endpoint."
                    )
                results.record_gas_price(self.url, self.client.cfx.gas_price)
                results.record_client_version(self.url, self.client.clientVersion)
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.url)))
                results.record_health(self.url, False)
        except asyncio.exceptions.TimeoutError:
            logger.info("Client timed out for {}".format(strip_url(self.url)))
            results.record_health(self.url, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
