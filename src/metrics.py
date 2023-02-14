"""A module that does does everything Prometheus related."""
from concurrent.futures import ThreadPoolExecutor
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily
from registries import CollectorRegistry


class MetricsLoader():
    """Central place to instantiate and manage all of the metric processed by the exporter.
    This is created so standardization is enforced in terms of metrics names, labels etc."""

    def __init__(self):
        self._labels = [
            'url', 'provider', 'blockchain', 'network_name', 'network_type',
            'chain_id'
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


class PrometheusCustomCollector():  # pylint: disable=too-few-public-methods
    """https://github.com/prometheus/client_python#custom-collectors"""

    def __init__(self):
        self._collector_registry = CollectorRegistry().get_collector_registry
        self._metrics_loader = MetricsLoader()

    def collect(self):
        """This method is called each time /metric is called."""
        health_metric = self._metrics_loader.health_metric
        heads_received_metric = self._metrics_loader.heads_received_metric
        disconnects_metric = self._metrics_loader.disconnects_metric
        block_height_metric = self._metrics_loader.block_height_metric
        client_version_metric = self._metrics_loader.client_version_metric
        total_difficulty_metric = self._metrics_loader.total_difficulty_metric
       
        def _write_metric(metric, metric_value):
            if metric_value is not None:
                metric.add_metric(collector.labels, metric_value)
    
        def _write_alive(collector):
                _write_metric(health_metric, collector.alive())

        def _write_disconnects(collector):
            if hasattr(collector, 'disconnects'):
                _write_metric(disconnects_metric, collector.disconnects())

        def _write_heads_received(collector):
            if hasattr(collector, 'heads_received'):
                _write_metric(heads_received_metric, collector.heads_received())

        def _write_block_height(collector):
            if hasattr(collector, 'block_height'):
                _write_metric(block_height_metric, collector.block_height())

        def _write_client_version(collector):
            if hasattr(collector, 'client_version'):
                _write_metric(client_version_metric, collector.client_version())

        def _write_total_difficulty(collector):
            if hasattr(collector, 'total_difficulty'):
                _write_metric(total_difficulty_metric, collector.total_difficulty())
        
        # Make sure that multiplier is always number of metrics implemented.
        multiplier = 6

        with ThreadPoolExecutor(        
                max_workers=len(self._collector_registry)*multiplier) as executor:
            for collector in self._collector_registry:
                #TODO: Make this work.
                collector.interface.cache.clear_cache()
                executor.submit(_write_alive, collector)
                executor.submit(_write_disconnects, collector)
                executor.submit(_write_heads_received, collector)
                executor.submit(_write_block_height, collector)
                executor.submit(_write_client_version, collector)
                executor.submit(_write_total_difficulty, collector)
                
                

                

        yield health_metric
        yield heads_received_metric
        yield disconnects_metric
        yield block_height_metric
        yield client_version_metric
        yield total_difficulty_metric
