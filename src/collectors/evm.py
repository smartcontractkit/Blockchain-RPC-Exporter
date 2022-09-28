from settings import cfg, logger
from web3 import Web3
from web3.exceptions import ExtraDataLengthError
import asyncio
from helpers import strip_url, check_protocol, generate_labels_from_metadata
from collectors.ws import websocket_collector
from websockets.exceptions import WebSocketException
from metrics_processor import results


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
            self.record_difficulty = True

        else:
            logger.error("Please provide wss/ws endpoint for {}".format(strip_url(self.url)))
            exit(1)

    def probe(self) -> results:
        try:
            if self.client.isConnected():
                results.register(self.url, self.labels_values)
                results.record_health(self.url, True)
                results.record_head_count(self.url, self.ws_collector.message_counter)
                results.record_disconnects(self.url, self.ws_collector.disconnects_counter)
                results.record_latency(self.url, self.ws_collector.get_latency())
                results.record_block_height(self.url, self.client.eth.block_number)
                try:
                    if self.record_difficulty:
                        results.record_total_difficulty(self.url, self.client.eth.get_block('latest')['totalDifficulty'])
                        results.record_difficulty(self.url, self.client.eth.get_block('latest')['difficulty'])
                except ExtraDataLengthError:
                    logger.info("It looks like this is a POA chain, and does not use difficulty anymore. Collector will ignore difficulty metric from this point on")
                    self.record_difficulty = False
                results.record_gas_price(self.url, self.client.eth.gas_price)
                results.record_max_priority_fee(self.url, self.client.eth.max_priority_fee)
                results.record_client_version(self.url, self.client.clientVersion)
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.url)))
                results.record_health(self.url, False)
        except asyncio.exceptions.TimeoutError as exc:
            logger.info("Client timed out for {}: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
        except WebSocketException as exc:
            logger.info("Websocket client exception {}: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            results.record_health(self.url, False)
