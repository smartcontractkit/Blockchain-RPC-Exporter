# pylint: disable=protected-access
"""Tests the metrics module"""
from unittest import TestCase, mock
from collections import namedtuple
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily

from metrics import MetricsLoader, PrometheusCustomCollector


class TestMetricsLoader(TestCase):
    """Tests the MetricsLoader class"""

    def setUp(self):
        self.metrics_loader = MetricsLoader()
        self.labels = [
            'url', 'provider', 'blockchain', 'network_name', 'network_type', 'evmChainID'
        ]

    def test_labels(self):
        """Tests that the metrics labels are set with correct naming and order"""
        self.assertEqual(
            self.labels, self.metrics_loader._labels)

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
                'brpc_client_version_info',
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

    def test_latency_metric(self):
        """Tests the latency_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.latency_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_latency',
                'Latency of the rpc connection.',
                labels=self.labels)

    def test_latency_metric_returns_gauge(self):
        """Tests the latency_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.latency_metric))

    def test_block_height_delta_metric(self):
        """Tests the block_height_delta_metric property calls GaugeMetric with the correct args"""
        with mock.patch('metrics.GaugeMetricFamily') as gauge_mock:
            self.metrics_loader.block_height_delta_metric  # pylint: disable=pointless-statement
            gauge_mock.assert_called_once_with(
                'brpc_block_height_behind_highest',
                'Difference between block heights relative to the max block height',
                labels=self.labels)

    def test_block_height_delta_metric_returns_gauge(self):
        """Tests the block_height_delta_metric property returns a gauge"""
        self.assertEqual(GaugeMetricFamily, type(
            self.metrics_loader.block_height_delta_metric))


class TestPrometheusCustomCollector(TestCase):
    """Tests the prometheus custom collector class"""

    def setUp(self):
        with (
            mock.patch("metrics.CollectorRegistry") as mocked_registry,
            mock.patch("metrics.MetricsLoader") as mocked_loader
        ):
            mocked_registry.return_value.get_collector_registry = [
                mock.Mock(), mock.Mock()]
            self.prom_collector = PrometheusCustomCollector()
            self.mocked_registry = mocked_registry
            self.mocked_loader = mocked_loader

    def test_collect_yields_correct_metrics(self):
        """Tests that the collect yields all the expected metrics"""
        expected_returns = [
            self.mocked_loader.return_value.health_metric,
            self.mocked_loader.return_value.heads_received_metric,
            self.mocked_loader.return_value.disconnects_metric,
            self.mocked_loader.return_value.block_height_metric,
            self.mocked_loader.return_value.client_version_metric,
            self.mocked_loader.return_value.total_difficulty_metric,
            self.mocked_loader.return_value.block_height_delta_metric,
            self.mocked_loader.return_value.latency_metric
        ]
        results = self.prom_collector.collect()
        for result in results:
            self.assertTrue(result in expected_returns)

    def test_collect_number_of_yields(self):
        """Tests that the collect method yields the expected number of values"""
        results = self.prom_collector.collect()
        self.assertEqual(8, len(list(results)))

    def test_get_thread_count(self):
        """Tests get thread count returns the expected number of threads
        based on number of metrics and collectors"""
        thread_count = self.prom_collector.get_thread_count()
        # Total of 8 metrics times 2 items in our mocked pool should give 16
        self.assertEqual(16, thread_count)

    def test_collect_thread_max_workers(self):
        """Tests the max workers is correct for the collect threads"""
        with mock.patch('metrics.ThreadPoolExecutor') as thread_pool_mock:
            # generator is added to a list to ensure it yields all results before assertion
            list(self.prom_collector.collect())
            # Threadpoolexecutor should be called with get_thread_count result.
            thread_count = self.prom_collector.get_thread_count()
            thread_pool_mock.assert_called_once_with(max_workers=thread_count)

    def test_write_metric_valid_value(self):
        """Test that the add_metric method is called when a valid metric value is present"""
        mocked_collector = mock.Mock()
        mocked_metric = mock.Mock()
        getattr(mocked_collector, 'attr').return_value = 20
        self.prom_collector._write_metric(
            mocked_collector, mocked_metric, 'attr')
        mocked_metric.add_metric.assert_called_once_with(
            mocked_collector.labels, 20)

    def test_write_metric_no_value(self):
        """Test that the add_metric method is not called when no metric value is present"""
        mocked_collector = mock.Mock()
        mocked_metric = mock.Mock()
        getattr(mocked_collector, 'attr').return_value = None
        self.prom_collector._write_metric(
            mocked_collector, mocked_metric, 'attr')
        mocked_metric.add_metric.assert_not_called()

    def test_collect_clears_cache_for_each_collector(self):
        """Tests that for each collector the cache is cleared"""
        # generator is added to a list to ensure it yields all results before assertion
        list(self.prom_collector.collect())
        for collector in self.prom_collector._collector_registry:
            collector.interface.cache.clear_cache.assert_called_once_with()

    def test_collect_alive(self):
        """Tests the alive metric is written using a thread for each collector"""
        with mock.patch('metrics.ThreadPoolExecutor') as thread_pool_mock:
            # generator is added to a list to ensure it yields all results before assertion
            list(self.prom_collector.collect())
            for collector in self.prom_collector._collector_registry:
                thread_pool_mock.return_value.__enter__.return_value.submit.assert_any_call(
                    self.prom_collector._write_metric,
                    collector,
                    self.mocked_loader.return_value.health_metric,
                    'alive')

    def test_delta_compared_to_max(self):
        """Tests the delta_compared_to_max method calculates the correct delta between metrics"""
        Metric = namedtuple('Metric', ['name', 'samples'])
        labels_one = {'url': 'test1.com', 'blockchain': 'test'}
        labels_two = {'url': 'test2.com', 'blockchain': 'test'}
        labels_three = {'url': 'test3.com', 'blockchain': 'test'}
        source_metric = Metric(name="dummy metric", samples=[
                               ['dummy sample 1', labels_one, 32],
                               ['dummy sample 2', labels_two, 10],
                               ['dummy sample 3', labels_three, 5]])
        mocked_target_metric = mock.Mock()
        expected_calls = [mock.call(list(labels_one.values()), 0),
                          mock.call(list(labels_two.values()), 22),
                          mock.call(list(labels_three.values()), 27)]

        self.prom_collector.delta_compared_to_max(
            source_metric, mocked_target_metric)
        mocked_target_metric.add_metric.assert_has_calls(
            expected_calls, any_order=True)
