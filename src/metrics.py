"""A module that does does everything Prometheus related."""
from concurrent.futures import ThreadPoolExecutor
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily
from prometheus_client import Histogram

from registries import CollectorRegistry


class MetricsLoader():
    """Central place to instantiate and manage all of the metric processed by the exporter.
    This is created so standardization is enforced in terms of metrics names, labels etc."""

    def __init__(self):
        self._labels = [
            'url', 'provider', 'blockchain', 'network_name', 'network_type',
            'evmChainID'
        ]

    @property
    def health_metric(self):
        """Returns instantiated health metric."""
        return GaugeMetricFamily(
            'brpc_health',
            'Returns 1 if rpc websocket server established a connection with the probe client.',
            labels=self._labels)

    @property
    def heads_received_metric(self):
        """Returns instantiated head count metric."""
        return CounterMetricFamily('brpc_head_count',
                                   'Heads received total.',
                                   labels=self._labels)

    @property
    def disconnects_metric(self):
        """Returns instantiated disconnects metric."""
        return GaugeMetricFamily('brpc_disconnects',
                                 'How many times rpc has disconnected.',
                                 labels=self._labels)

    @property
    def block_height_metric(self):
        """Returns instantiated block height metric."""
        return GaugeMetricFamily('brpc_block_height',
                                 'Latest observed block_height.',
                                 labels=self._labels)

    @property
    def client_version_metric(self):
        """Returns instantiated client version metric."""
        return InfoMetricFamily(
            'brpc_client_version',
            'Client version for the particular RPC endpoint.',
            labels=self._labels)

    @property
    def total_difficulty_metric(self):
        """Returns instantiated total difficulty metric."""
        return GaugeMetricFamily(
            'brpc_total_difficulty',
            'Total canonical chain difficulty observed from the first to the latest block.',
            labels=self._labels)

    @property
    def latency_metric(self):
        """Returns instantiated latency metric."""
        return GaugeMetricFamily(
            'brpc_latency',
            'Returns latency of the rpc connection.',
            labels=self._labels)

    def universal_gauge(self, metric_name, helper_string):
        """Returns instantiated total difficulty metric."""
        return GaugeMetricFamily(
            metric_name, helper_string,
            labels=self._labels)


class PrometheusCustomCollector():  # pylint: disable=too-few-public-methods
    """https://github.com/prometheus/client_python#custom-collectors"""

    def __init__(self):
        self._collector_registry = CollectorRegistry().get_collector_registry
        self._metrics_loader = MetricsLoader()

    def _write_metric(self, collector, metric, attribute):
        """Gets metric from collector and writes it"""
        if hasattr(collector, attribute):
            metric_value = getattr(collector, attribute)()
            if metric_value is not None:
                metric.add_metric(collector.labels, metric_value)

    def get_thread_count(self) -> int:
        size_of_pool = len(self._collector_registry)
        number_of_metrics = len(
            [attr for attr in MetricsLoader.__dict__.values() if isinstance(attr, property)])
        return size_of_pool * number_of_metrics

    # We know.
    def delta_compared_to_max(self, source_metric, target_metric_name):
        metric = self._metrics_loader.universal_gauge(
            target_metric_name, 'This metrics finds delta for a target metric.')
        highest = 0
        for sample in source_metric.samples:
            if sample[2] > highest:
                highest = sample[2]
        for sample in source_metric.samples:
            delta = highest - sample[2]
            metric.add_metric(sample[1].values(), delta)
        return metric

    def collect(self):
        """This method is called each time /metric is called."""
        health_metric = self._metrics_loader.health_metric
        heads_received_metric = self._metrics_loader.heads_received_metric
        disconnects_metric = self._metrics_loader.disconnects_metric
        block_height_metric = self._metrics_loader.block_height_metric
        client_version_metric = self._metrics_loader.client_version_metric
        total_difficulty_metric = self._metrics_loader.total_difficulty_metric
        latency_metric = self._metrics_loader.latency_metric

        with ThreadPoolExecutor(
                max_workers=self.get_thread_count()) as executor:
            for collector in self._collector_registry:
                collector.interface.cache.clear_cache()
                executor.submit(self._write_metric, collector,
                                health_metric, 'alive')
                executor.submit(self._write_metric, collector,
                                client_version_metric, 'client_version')
                executor.submit(self._write_metric, collector,
                                block_height_metric, 'block_height')
                executor.submit(self._write_metric, collector,
                                heads_received_metric, 'heads_received')
                executor.submit(self._write_metric, collector,
                                disconnects_metric, 'disconnects')
                executor.submit(self._write_metric, collector,
                                total_difficulty_metric, 'total_difficulty')
        for collector in self._collector_registry:
            self._write_metric(collector, latency_metric, 'latency')
        block_height_delta_metric = self.delta_compared_to_max(
            block_height_metric, 'brpc_block_height_behind_latest')

        yield health_metric
        yield heads_received_metric
        yield disconnects_metric
        yield block_height_metric
        yield client_version_metric
        yield total_difficulty_metric
        yield block_height_delta_metric
        yield latency_metric
