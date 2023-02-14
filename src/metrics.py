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
        self._metric_names = ["alive", "disconnects", "heads_received",
                              "block_height", "client_version", "total_difficulty"]

    def collect(self):
        """This method is called each time /metric is called."""
        health_metric = self._metrics_loader.health_metric
        heads_received_metric = self._metrics_loader.heads_received_metric
        disconnects_metric = self._metrics_loader.disconnects_metric
        block_height_metric = self._metrics_loader.block_height_metric
        client_version_metric = self._metrics_loader.client_version_metric
        total_difficulty_metric = self._metrics_loader.total_difficulty_metric

        def _write_metrics(collector, futures_dict):
            alive = futures_dict["alive"].result()
            del futures_dict["alive"]
            health_metric.add_metric(collector.labels, alive)
            if alive:
                for name_key, future in futures_dict.items():
                    result = future.result()
                    if result is not None:
                        match name_key:
                            case "disconnects":
                                disconnects_metric.add_metric(
                                    collector.labels, result)
                            case "heads_received":
                                heads_received_metric.add_metric(
                                    collector.labels, result)
                            case "block_height":
                                block_height_metric.add_metric(
                                    collector.labels, result)
                            case "client_version":
                                client_version_metric.add_metric(collector.labels, value={
                                    "client_version": result})
                            case "total_difficulty":
                                total_difficulty_metric.add_metric(
                                    collector.labels, result)
            else:
                for future in futures_dict.values():
                    future.cancel()
            collector.invalidate_cache()

        with ThreadPoolExecutor(
                max_workers=len(self._collector_registry) * len(self._metric_names)) as executor:
            for collector in self._collector_registry:
                futures_dict = {}
                for metric_name in self._metric_names:
                    metric_call = getattr(collector, metric_name, None)
                    if metric_call is not None:
                        futures_dict[metric_name] = executor.submit(
                            metric_call)
                executor.submit(_write_metrics, collector, futures_dict)

        yield health_metric
        yield heads_received_metric
        yield disconnects_metric
        yield block_height_metric
        yield client_version_metric
        yield total_difficulty_metric
