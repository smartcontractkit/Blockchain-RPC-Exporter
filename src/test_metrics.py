"""Tests the metrics module"""
from unittest import TestCase, mock
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily

from metrics import MetricsLoader, PrometheusCustomCollector


class TestMetricsLoader(TestCase):
    """Tests the MetricsLoader class"""

    def setUp(self):
        self.metrics_loader = MetricsLoader()
        self.labels = [
            'url', 'provider', 'blockchain', 'network_name', 'network_type', 'chain_id'
        ]

    def test_labels(self):
        """Tests that the metrics labels are set with correct naming and order"""
        self.assertEqual(
            self.labels, self.metrics_loader._labels)  # pylint: disable=protected-access

    def test_health_metric(self):
        """Tests the health_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.health_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_health',
                'Returns 1 if rpc websocket server established a connection with the probe client.',
                labels=self.labels)

    def test_health_metric_returns_gauge(self):
        """Tests the health_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.health_metric))

    def test_heads_received_metric(self):
        """Tests the heads_received_metric property calls CounterMetric with the correct args"""
        with mock.patch('metrics.CounterMetricFamily') as counter_mock:
            self.metrics_loader.heads_received_metric  # pylint: disable=pointless-statement
            counter_mock.assert_called_once_with(
                'brpc_head_count',
                'Heads received total.',
                labels=self.labels)

    def test_heads_received_metric_returns_counter(self):
        """Tests the heads_received_metric property returns a counter"""
        self.assertEqual(CounterMetricFamily, type(
            self.metrics_loader.heads_received_metric))

    def test_disconnects_metric(self):
        """Tests the disconnects_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.disconnects_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_disconnects',
                'How many times rpc has disconnected.',
                labels=self.labels)

    def test_disconnects_metric_returns_gauge(self):
        """Tests the disconnects_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.disconnects_metric))

    def test_block_height_metric(self):
        """Tests the block_height_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.block_height_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_block_height',
                'Latest observed block_height.',
                labels=self.labels)

    def test_block_height_metric_returns_gauge(self):
        """Tests the block_height_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.block_height_metric))

    def test_client_version_metric(self):
        """Tests the client_version_metric property calls InfoMetric with the correct args"""
        with mock.patch('metrics.InfoMetricFamily') as info_mock:
            self.metrics_loader.client_version_metric  # pylint: disable=pointless-statement
            info_mock.assert_called_once_with(
                'brpc_client_version',
                'Client version for the particular RPC endpoint.',
                labels=self.labels)

    def test_client_version_metric_returns_gauge(self):
        """Tests the client_version_metric property returns a gauge"""
        self.assertEqual(InfoMetricFamily, type(
            self.metrics_loader.client_version_metric))

    def test_total_difficulty_metric(self):
        """Tests the total_difficulty_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.total_difficulty_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_total_difficulty',
                'Total canonical chain difficulty observed from the first to the latest block.',
                labels=self.labels)

    def test_total_difficulty_metric_returns_gauge(self):
        """Tests the total_difficulty_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.total_difficulty_metric))


class TestPrometheusCustomCollector(TestCase):
    """Tests the prometheus custom collector class"""

    def setUp(self):
        with (
            mock.patch("metrics.CollectorRegistry") as mocked_registry,
            mock.patch("metrics.MetricsLoader") as mocked_loader
        ):
            mocked_registry.return_value.get_collector_registry = [mock.Mock()]
            self.prom_collector = PrometheusCustomCollector()
            self.mocked_registry = mocked_registry
            self.mocked_loader = mocked_loader

    def test_collect_metric_names(self):
        """Tests that the collect method has the correct values in metric_names list"""
        names = ["alive", "disconnects", "heads_received",
                 "block_height", "client_version", "total_difficulty"]
        self.assertEqual(
            names, self.prom_collector._metric_names)  # pylint: disable=protected-access

    def test_collect_yields_correct_metrics(self):
        """Tests that the collect yields all the expected metrics"""
        expected_returns = [
            self.mocked_loader.return_value.health_metric,
            self.mocked_loader.return_value.heads_received_metric,
            self.mocked_loader.return_value.disconnects_metric,
            self.mocked_loader.return_value.block_height_metric,
            self.mocked_loader.return_value.client_version_metric,
            self.mocked_loader.return_value.total_difficulty_metric
        ]
        results = self.prom_collector.collect()
        for result in results:
            self.assertTrue(result in expected_returns)

    def test_collect_number_of_yields(self):
        """Tests that the collect method yields the expected number of values"""
        results = self.prom_collector.collect()
        self.assertEqual(6, len(list(results)))
