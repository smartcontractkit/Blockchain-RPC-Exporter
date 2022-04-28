import os
import logging

from prometheus_client import REGISTRY, make_wsgi_app
from prometheus_client.metrics_core import GaugeMetricFamily, CounterMetricFamily
from wsgiref.simple_server import make_server

import settings
from probe import rpc_probe

from concurrent.futures import ThreadPoolExecutor

LOGLEVEL = settings.LOGLEVEL
logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(message)s')


class metrics_registry(object):

    def __init__(self, collector=None):
        if not collector:
            collector = rpc_probe(uris=settings.RPCS,
                                  timeout=settings.TIMEOUT,
                                  chain_id=settings.CHAIN_ID)
            collector.setDaemon(True)
            collector.start()

        self._collector = collector

    def _highest_in_results(self, results: list, target_key: str):
        highest = 0
        for key in results:
            obs_value = key[target_key]
            if obs_value > highest:
                highest = obs_value
        return highest

    def collect(self):
        metric_labels = [
            'url', 'blockchain', 'network_name', 'network_type', 'url',
            'provider'
        ]

        up_metric = GaugeMetricFamily('ws_rpc_health',
                                      '1 for up 0 for down',
                                      labels=metric_labels)
        block_height_metric = GaugeMetricFamily('ws_rpc_block_height',
                                                'Latest observed block_height',
                                                labels=metric_labels)

        total_difficulty_metric = GaugeMetricFamily(
            'ws_rpc_total_difficulty',
            'Total difficulty observed from the latest block.',
            labels=metric_labels)

        latency_metric = GaugeMetricFamily(
            'ws_rpc_latency',
            'Latency of a perticular RPC endpoint',
            labels=metric_labels)

        behind_highest_metric_difficulty = GaugeMetricFamily(
            'ws_rpc_difficulty_behind_highest',
            'How much latest block a perticular node deviates from latest observed totalDifficulty in the pool.',
            labels=metric_labels)

        behind_highest_metric_blocks = GaugeMetricFamily(
            'ws_rpc_block_height_behind_highest',
            'How much blocks a perticular node deviates from highest observed',
            labels=metric_labels)

        head_count_metric = CounterMetricFamily(
            'ws_rpc_head_count',
            'Count of heads received for a perticular rpc endpoint',
            labels=metric_labels)

        disconnect_counter_metric = CounterMetricFamily(
            'ws_rpc_disconnects',
            'How many times rpc has disconnected from the server side',
            labels=metric_labels)

        within_sla_metric = GaugeMetricFamily(
            'ws_rpc_sla_compliant',
            'Based on block height divergence,latency and health, reports 1 for compliant and 0 for non compliant',
            labels=metric_labels)

        def _record_metrics(record):
            obs_url = record['url']
            obs_provider = record['provider']
            obs_up = record['up']
            obs_block_height = record['block_height']
            obs_total_difficulty = record['total_difficulty']
            obs_latency = record['latency']
            obs_head_count = head_counts[obs_url]
            obs_disconnects_count = disconnect_counts[obs_url]
            total_difficulty_deviation = highest_difficulty - record[
                'total_difficulty']
            block_deviation = highest_block - record['block_height']

            labels = [
                obs_url, settings.BLOCKCHAIN, settings.NETWORK_NAME,
                settings.NETWORK_TYPE, obs_url, obs_provider
            ]

            if obs_up:
                if obs_latency < settings.MAX_RESPONSE_LATENCY_MILISECONDS and block_deviation < settings.MAX_POOL_DEVIATION_BLOCK_COUNT:
                    within_sla_metric.add_metric(labels, 1)
                else:
                    within_sla_metric.add_metric(labels, 0)
                up_metric.add_metric(labels, obs_up)
                block_height_metric.add_metric(labels, obs_block_height)
                total_difficulty_metric.add_metric(labels,
                                                   obs_total_difficulty)
                behind_highest_metric_difficulty.add_metric(
                    labels, total_difficulty_deviation)
                behind_highest_metric_blocks.add_metric(
                    labels, block_deviation)
                latency_metric.add_metric(labels, obs_latency)
                head_count_metric.add_metric(labels, obs_head_count)
                disconnect_counter_metric.add_metric(labels,
                                                     obs_disconnects_count)
            else:
                up_metric.add_metric(labels, obs_up)

        results = self._collector.get_results()
        highest_block = self._highest_in_results(results, 'block_height')
        highest_difficulty = self._highest_in_results(results,
                                                      'total_difficulty')

        head_counts = self._collector.head_counter
        disconnect_counts = self._collector.disconnects_counter

        logging.debug("Results: {}".format(results))
        logging.debug("Highest block: {}".format(highest_block))
        logging.debug("Log counts: {}".format(head_counts))
        logging.debug("Disconnect counts: {}".format(disconnect_counts))

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(_record_metrics, results)

        yield up_metric
        yield block_height_metric
        yield total_difficulty_metric
        yield behind_highest_metric_difficulty
        yield latency_metric
        yield behind_highest_metric_blocks
        yield head_count_metric
        yield disconnect_counter_metric
        yield within_sla_metric


def dummy_report(environ, start_fn):
    start_fn('200 OK', [])
    return [b'Service seems to be up and serving requests.']


def my_app(environ, start_fn):
    if environ['PATH_INFO'] == '/metrics':
        return metrics_app(environ, start_fn)
    # TODO: Write an actuall liveness and readiness probes.
    if environ['PATH_INFO'] == '/readiness':
        return dummy_report(environ, start_fn)
    if environ['PATH_INFO'] == '/liveness':
        return dummy_report(environ, start_fn)


if __name__ == '__main__':
    REGISTRY.register(metrics_registry())
    metrics_app = make_wsgi_app()
    httpd = make_server('', 8000, my_app)
    httpd.serve_forever()
