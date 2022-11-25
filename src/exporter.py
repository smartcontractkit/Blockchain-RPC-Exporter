from concurrent.futures import ThreadPoolExecutor
from prometheus_client import REGISTRY, make_wsgi_app
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily
from wsgiref.simple_server import make_server
from collectors.evm import evm_collector
from collectors.solana import solana_collector
from collectors.cardano import cardano_collector
from collectors.conflux import conflux_collector
from collectors.bitcoin import bitcoin_collector
from collectors.filecoin import filecoin_collector
from collectors.starkware import starkware_collector
from settings import logger
from helpers import cfg
from metrics_processor import results


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
        if cfg.isFilecoin():
            self._instantiate_filecoin()
        if cfg.isStarkware():
            self._instantiate_starkware()

    def _instantiate_evm(self):
        for item in cfg.endpoints:
            logger.info("Initializing evm node")
            self.collectors.append(evm_collector(item))
        self.labels = self.collectors[0].labels

    def _instantiate_conflux(self):
        for item in cfg.endpoints:
            logger.info("Initializing conflux node")
            self.collectors.append(conflux_collector(item))
        self.labels = self.collectors[0].labels

    def _instantiate_solana(self):
        for item in cfg.endpoints:
            logger.info("Initializing solana node")
            self.collectors.append(solana_collector(item))
        self.labels = self.collectors[0].labels

    def _instantiate_cardano(self):
        for item in cfg.endpoints:
            logger.info("Initializing cardano node")
            self.collectors.append(cardano_collector(item))
            self.labels = self.collectors[0].labels

    def _instantiate_bitcoin(self):
        for item in cfg.endpoints:
            logger.info("Initializing bitcoin node.")
            self.collectors.append(bitcoin_collector(item))
            self.labels = self.collectors[0].labels

    def _instantiate_doge(self):
        for item in cfg.endpoints:
            logger.info("Initializing doge node")
            self.collectors.append(bitcoin_collector(item))
            self.labels = self.collectors[0].labels

    def _instantiate_filecoin(self):
        for item in cfg.endpoints:
            logger.info("Initializing filecoin node")
            self.collectors.append(filecoin_collector(item))
            self.labels = self.collectors[0].labels

    def _instantiate_starkware(self):
        for item in cfg.endpoints:
            logger.info("Initializing starkware node")
            self.collectors.append(starkware_collector(item))
            self.labels = self.collectors[0].labels

    def _report_exporter_health(self, health_metric):
        health_metric.add_metric([cfg.blockchain], True)

    def collect(self):
        metrics = {
            "brpc_health":
            GaugeMetricFamily('brpc_health',
                              'Returns 1 if rpc websocket server established a connection with the probe client.',
                              labels=self.labels),
            "brpc_latency":
            GaugeMetricFamily('brpc_latency',
                              'Latency in milliseconds of the websocket keepalive ping.',
                              labels=self.labels),
            "brpc_disconnects":
            GaugeMetricFamily('brpc_disconnects', 'How many times rpc has disconnected.', labels=self.labels),
            "brpc_block_height":
            GaugeMetricFamily('brpc_block_height', 'Latest observed block_height.', labels=self.labels),
            "brpc_head_count":
            CounterMetricFamily('brpc_head_count', 'Heads received total.', labels=self.labels),
            "brpc_difficulty":
            GaugeMetricFamily('brpc_difficulty', 'Difficulty of the latest observed block.', labels=self.labels),
            "brpc_total_difficulty":
            GaugeMetricFamily('brpc_total_difficulty',
                              'Total canonical chain difficulty observed from the first to the latest block.',
                              labels=self.labels),
            "brpc_gas_price":
            GaugeMetricFamily('brpc_gas_price', 'The current gas price in Wei.', labels=self.labels),
            "brpc_max_priority_fee":
            GaugeMetricFamily('brpc_max_priority_fee',
                              'Suggested max priority fee for dynamic fee transactions in Wei.',
                              labels=self.labels),
            "brpc_net_peer_count":
            GaugeMetricFamily('brpc_net_peer_count',
                              'Number of peers currently connected to the client.',
                              labels=self.labels),
            "brpc_client_version":
            InfoMetricFamily('brpc_client_version',
                             'Client version for the particular RPC endpoint.',
                             labels=self.labels),
            "brpc_block_height_behind_highest":
            GaugeMetricFamily('brpc_block_height_behind_highest',
                              'Number of blocks behind highest in the pool.',
                              labels=self.labels),
            "brpc_difficulty_behind_highest":
            GaugeMetricFamily('brpc_difficulty_behind_highest',
                              'Delta compared between highest total difficulty of the latest block in the pool.',
                              labels=self.labels),
        }

        def collect_metrics(prom_collector):
            prom_collector.probe()

        with ThreadPoolExecutor(max_workers=len(self.collectors)) as executor:
            for collector in self.collectors:
                executor.submit(collect_metrics, collector)
        # Process the collected metrics
        results.write_metrics(metrics)

        for _, metric in metrics.items():
            # Only yield metric if samples were provided by the probe
            if len(metric.samples) > 0:
                yield metric
        # The last step is to report exporter health
        # This metric will be used to monitor if exporter is alive and forwarding metrics to prometheus endpoints.
        exporter_health_metric = GaugeMetricFamily(
            'brpc_exporter_health',
            'Returns 1 if exporter was able to finalise scraping loop without exceptions.',
            labels=['blockchain'])
        self._report_exporter_health(exporter_health_metric)
        yield exporter_health_metric


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
