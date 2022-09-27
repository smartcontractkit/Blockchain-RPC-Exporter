from settings import cfg, logger
from conflux_web3 import Web3
import asyncio
from helpers import strip_url, validate_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector


class conflux_collector():

    def __init__(self, rpc_metadata):
        validate_protocol(rpc_metadata['url'], "wss")
        self.url = rpc_metadata['url']
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

    def probe(self, metrics):
        try:
            if self.client.isConnected():
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['brpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['brpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['brpc_block_height'].add_metric(self.labels_values, self.client.cfx.epoch_number)

                try:
                    difficulty = self.client.cfx.get_block_by_hash(self.client.cfx.get_best_block_hash())['difficulty']
                    metrics['brpc_difficulty'].add_metric(self.labels_values, difficulty)
                except TypeError:
                    logger.error(
                        "RPC Endpoint sent faulty response type when querying for difficulty. This is most likely issue with RPC endpoint."
                    )

                metrics['brpc_gas_price'].add_metric(self.labels_values, self.client.cfx.gas_price)
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.url)))
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except asyncio.exceptions.TimeoutError:
            logger.info("Client timed out for {}".format(strip_url(self.url)))
            metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
