from settings import cfg, logger
from conflux_web3 import Web3
import asyncio
from helpers import strip_url
from collectors.ws import websocket_collector


class conflux_collector():

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
                                                    "method": "cfx_subscribe",
                                                    "jsonrpc": "2.0",
                                                    "id": 1,
                                                    "params": ["newHeads"]
                                                })
        self.ws_collector.setDaemon(True)
        self.ws_collector.start()
        self.first_time = False

    def probe(self, metrics):
        try:
            if self.client.isConnected():
                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_head_count'].add_metric(self.labels_values, self.ws_collector.message_counter)
                metrics['ws_rpc_disconnects'].add_metric(self.labels_values, self.ws_collector.disconnects_counter)
                metrics['ws_rpc_latency'].add_metric(self.labels_values, self.ws_collector.get_latency())
                metrics['ws_rpc_block_height'].add_metric(self.labels_values, self.client.cfx.epoch_number)

                metrics['ws_rpc_difficulty'].add_metric(
                    self.labels_values,
                    self.client.cfx.get_block_by_hash(self.client.cfx.get_best_block_hash())['difficulty'])

                metrics['ws_rpc_gas_price'].add_metric(self.labels_values, self.client.cfx.gas_price)
            else:
                logger.info("Client is not connected to {}".format(strip_url(self.websocket_url)))
                metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except asyncio.exceptions.TimeoutError:
            logger.info("Client timed out for {}".format(strip_url(self.websocket_url)))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)
        except Exception as e:
            logger.error("Error while probing {}".format(strip_url(self.websocket_url)))