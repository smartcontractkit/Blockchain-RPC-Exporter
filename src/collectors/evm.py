from settings import cfg, logger
from web3 import Web3
import asyncio
from helpers import strip_url
from collectors.ws import websocket_collector
from websockets.exceptions import WebSocketException

class evm_collector():

    def __init__(self, websocket_url, https_url, provider):
        self.client = Web3(Web3.WebsocketProvider(websocket_url, websocket_timeout=cfg.response_timeout))
        self.labels = [
            'websocket_url', 'https_url', 'provider', 'blockchain', 'network_name', 'network_type', 'evmChainID'
        ]
        self.labels_values = [
            websocket_url, https_url, provider, cfg.blockchain, cfg.network_name, cfg.network_type,
            str(cfg.chain_id)
        ]
        self.websocket_url = websocket_url
        self.ws_collector = websocket_collector(websocket_url,
                                                sub_payload={
                                                    "method": "eth_subscribe",
                                                    "jsonrpc": "2.0",
                                                    "id": cfg.chain_id,
                                                    "params": ["newHeads"]
                                                })
        self.ws_collector.setDaemon(True)
        self.ws_collector.start()

    def probe(self, metrics):        
        try:
            if self.client.isConnected():
                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['ws_rpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['ws_rpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['ws_rpc_block_height'].add_metric(self.labels_values, self.client.eth.block_number)
                metrics['ws_rpc_total_difficulty'].add_metric(self.labels_values,
                                                              self.client.eth.get_block('latest')['totalDifficulty'])
                metrics['ws_rpc_difficulty'].add_metric(self.labels_values,
                                                        self.client.eth.get_block('latest')['difficulty'])
                metrics['ws_rpc_net_peer_count'].add_metric(self.labels_values, self.client.net.peer_count)
                metrics['ws_rpc_gas_price'].add_metric(self.labels_values, self.client.eth.gas_price)
                metrics['ws_rpc_max_priority_fee'].add_metric(self.labels_values, self.client.eth.max_priority_fee)
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.websocket_url)))
                metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except asyncio.exceptions.TimeoutError as exc:
            logger.info("Client timed out for {}: {}".format(strip_url(self.websocket_url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except WebSocketException as exc:
            logger.info("Websocket client exception {}: {}".format(strip_url(self.websocket_url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(strip_url(self.url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
