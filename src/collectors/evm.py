from settings import cfg, logger
from web3 import Web3
import asyncio
from helpers import strip_url, check_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector
from websockets.exceptions import WebSocketException


class evm_collector():

    def __init__(self, rpc_metadata):
        self.url = rpc_metadata['url']
        if check_protocol(rpc_metadata['url'], "wss") or check_protocol(rpc_metadata['url'], 'ws'):
            self.client = Web3(Web3.WebsocketProvider(self.url, websocket_timeout=cfg.response_timeout))

            self.labels, self.labels_values = generate_labels_from_metadata(rpc_metadata)

            self.ws_collector = websocket_collector(self.url,
                                                    sub_payload={
                                                        "method": "eth_subscribe",
                                                        "jsonrpc": "2.0",
                                                        "id": rpc_metadata['chain_id'],
                                                        "params": ["newHeads"]
                                                    })
            self.ws_collector.setDaemon(True)
            self.ws_collector.start()
        else:
            logger.error("Please provide wss/ws endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def probe(self, metrics):
        try:
            if self.client.isConnected():
                metrics['brpc_health'].add_metric(self.labels_values, True)
                metrics['brpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['brpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['brpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['brpc_block_height'].add_metric(self.labels_values, self.client.eth.block_number)
                metrics['brpc_total_difficulty'].add_metric(self.labels_values,
                                                            self.client.eth.get_block('latest')['totalDifficulty'])
                metrics['brpc_difficulty'].add_metric(self.labels_values,
                                                      self.client.eth.get_block('latest')['difficulty'])
                metrics['brpc_gas_price'].add_metric(self.labels_values, self.client.eth.gas_price)
                metrics['brpc_max_priority_fee'].add_metric(self.labels_values, self.client.eth.max_priority_fee)
                metrics['brpc_client_version'].add_metric(self.labels_values,
                                                          value={"client_version": self.client.clientVersion})
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.url)))
                metrics['brpc_health'].add_metric(self.labels_values, False)
        except asyncio.exceptions.TimeoutError as exc:
            logger.info("Client timed out for {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
        except WebSocketException as exc:
            logger.info("Websocket client exception {}: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            metrics['brpc_health'].add_metric(self.labels_values, False)
