from concurrent.futures import ThreadPoolExecutor
from prometheus_client import REGISTRY, make_wsgi_app
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily
from wsgiref.simple_server import make_server
from helpers import strip_url
from collectors.evm import evm_collector
from collectors.solana import solana_collector
from collectors.cardano import cardano_collector
from collectors.conflux import conflux_collector
from collectors.bitcoin import bitcoin_collector
from collectors.dogecoin import doge_collector
from settings import logger, cfg


class prom_registry(object):

    def __init__(self):
        self.collectors = []
        self.labels = []

        if cfg.isEvm():
            self._instantiate_evm()
        if cfg.isSolana():
            self._instantiate_solana()
        if cfg.isCardano():
            self._instantiate_cardano()
        if cfg.isConflux():
            self._instantiate_conflux()
        if cfg.isBitcoin():
            self._instantiate_bitcoin()
        if cfg.isDoge():
            self._instantiate_doge()

    def _instantiate_evm(self):
        for item in cfg.endpoints:
            logger.info("Initializing evm node {}".format(
                strip_url(item['ws_url'])))
            self.collectors.append(
                evm_collector(item['ws_url'], item['https_url'],
                              item['provider']))
        self.labels = self.collectors[0].labels

    def _instantiate_conflux(self):
        for item in cfg.endpoints:
            logger.info("Initializing conflux node {}".format(
                strip_url(item['ws_url'])))
            self.collectors.append(
                conflux_collector(item['ws_url'], item['https_url'],
                                  item['provider']))
        self.labels = self.collectors[0].labels

    def _instantiate_solana(self):
        for item in cfg.endpoints:
            logger.info("Initializing solana node {}".format(
                strip_url(item['https_url'])))
            self.collectors.append(
                solana_collector(item['ws_url'], item['https_url'],
                                 item['provider']))
        self.labels = self.collectors[0].labels

    def _instantiate_cardano(self):
        for item in cfg.endpoints:
            logger.info("Initializing cardano node {}".format(
                strip_url(item['ws_url'])))
            self.collectors.append(
                cardano_collector(item['ws_url'], item['provider']))
            self.labels = self.collectors[0].labels

    def _instantiate_bitcoin(self):
        for item in cfg.endpoints:
            logger.info("Initializing bitcoin node {}".format(
                strip_url(item['https_url'])))
            self.collectors.append(
                bitcoin_collector(item['https_url'], item['provider']))
            self.labels = self.collectors[0].labels

    def _instantiate_doge(self):
        for item in cfg.endpoints:
            logger.info("Initializing doge node {}".format(
                strip_url(item['https_url'])))
            self.collectors.append(
                doge_collector(item['https_url'], item['provider']))
            self.labels = self.collectors[0].labels

    def collect(self):
        metrics = {
            "ws_rpc_health":
            GaugeMetricFamily(
                'ws_rpc_health',
                'Returns 1 if rpc websocket server established a connection with the probe client.',
                labels=self.labels),
            "ws_rpc_latency":
            GaugeMetricFamily(
                'ws_rpc_latency',
                'Latency in milliseconds of the websocket keepalive ping.',
                labels=self.labels),
            "ws_rpc_disconnects":
            GaugeMetricFamily('ws_rpc_disconnects',
                              'How many times rpc has disconnected.',
                              labels=self.labels),
            "ws_rpc_block_height":
            GaugeMetricFamily('ws_rpc_block_height',
                              'Latest observed block_height.',
                              labels=self.labels),
            "ws_rpc_head_count":
            CounterMetricFamily('ws_rpc_head_count',
                                'Heads received total.',
                                labels=self.labels),
            "ws_rpc_difficulty":
            GaugeMetricFamily('ws_rpc_difficulty',
                              'Difficulty of the latest observed block.',
                              labels=self.labels),
            "ws_rpc_total_difficulty":
            GaugeMetricFamily(
                'ws_rpc_total_difficulty',
                'Total canonical chain difficulty observed from the first to the latest block.',
                labels=self.labels),
            "ws_rpc_gas_price":
            GaugeMetricFamily('ws_rpc_gas_price',
                              'The current gas price in Wei.',
                              labels=self.labels),
            "ws_rpc_max_priority_fee":
            GaugeMetricFamily(
                'ws_rpc_max_priority_fee',
                'Suggested max priority fee for dynamic fee transactions in Wei.',
                labels=self.labels),
            "ws_rpc_net_peer_count":
            GaugeMetricFamily(
                'ws_rpc_net_peer_count',
                'Number of peers currently connected to the client.',
                labels=self.labels)
        }

        def write_metrics(prom_collector, metrics):
            prom_collector.probe(metrics)

        with ThreadPoolExecutor(max_workers=len(self.collectors)) as executor:
            for collector in self.collectors:
                executor.submit(write_metrics, collector, metrics)

        for _, metric in metrics.items():
            # Only yield metric if samples were provided by the probe
            if len(metric.samples) > 0:
                yield metric


def dummy_report(environ, start_fn):
    start_fn('200 OK', [])
    return [b'Service seems to be up and serving requests.']


def my_app(environ, start_fn):
    if environ['PATH_INFO'] == '/metrics':
        return metrics_app(environ, start_fn)
    if environ['PATH_INFO'] == '/readiness':
        return dummy_report(environ, start_fn)
    if environ['PATH_INFO'] == '/liveness':
        return dummy_report(environ, start_fn)


if __name__ == '__main__':
    REGISTRY.register(prom_registry())
    logger.info("Started app")
    metrics_app = make_wsgi_app()
    httpd = make_server('', 8000, my_app)
    httpd.serve_forever()
