from src.metrics_processor import ProbeResults
import unittest
from unittest.mock import MagicMock, call

TEST_LABELS = ['url', 'provider', 'blockchain', 'network_name', 'network_type']


class test_metrics_processor(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.test_results = ProbeResults()
        self.TEST_LABEL_VALUES_1 = [
            'test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'
        ]
        self.TEST_LABEL_VALUES_2 = [
            'test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'
        ]
        self.TEST_LABEL_VALUES_3 = [
            'test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'
        ]
        self.test_results.register('test1.com', self.TEST_LABEL_VALUES_1)
        self.test_results.register('test2.com', self.TEST_LABEL_VALUES_2)
        self.test_results.register('test3.com', self.TEST_LABEL_VALUES_3)

    def test_register(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.assertEqual(self.test_results.metadata, expected_metadata)

    def test_record_health(self):
        expected_metadata_test1_healthy = {
            'test1.com': {
                'brpc_health': 1,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        expected_metadata_test1_unhealthy = {
            'test1.com': {
                'brpc_health': 0,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }

        self.test_results.record_health('test1.com', True)
        self.assertEqual(self.test_results.metadata, expected_metadata_test1_healthy)

        self.test_results.record_health('test1.com', False)
        self.assertEqual(self.test_results.metadata, expected_metadata_test1_unhealthy)

    def test_record_head_count(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': 123,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_head_count('test1.com', 123)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_disconnects(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': 123,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_disconnects('test1.com', 123)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_latency(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': 1.23,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_latency('test1.com', 1.23)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_block_height(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': 123,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_block_height('test1.com', 123)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_total_difficulty(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': 123,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_total_difficulty('test1.com', 123)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_difficulty(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': 123,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_difficulty('test1.com', 123)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_gas_price(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': 1.23,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_gas_price('test1.com', 1.23)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_max_priority_fee(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': 1.23,
                'brpc_client_version': None,
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_max_priority_fee('test1.com', 1.23)
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_record_client_version(self):
        expected_metadata = {
            'test1.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': 'Client123',
                'label_values':
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test2.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            },
            'test3.com': {
                'brpc_health': None,
                'brpc_head_count': None,
                'brpc_disconnects': None,
                'brpc_latency': None,
                'brpc_block_height': None,
                'brpc_difficulty': None,
                'brpc_total_difficulty': None,
                'brpc_gas_price': None,
                'brpc_max_priority_fee': None,
                'brpc_client_version': None,
                'label_values':
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type']
            }
        }
        self.test_results.record_client_version('test1.com', 'Client123')
        self.assertEqual(expected_metadata, self.test_results.metadata)

    def test_get_highest_block(self):
        self.test_results.record_block_height('test1.com', 123)
        self.test_results.record_block_height('test2.com', 124)
        self.test_results.record_block_height('test3.com', 125)
        self.assertEqual(self.test_results.get_highest_block(), 125)

    def test_get_highest_total_difficulty(self):
        self.test_results.record_total_difficulty('test1.com', 123)
        self.test_results.record_total_difficulty('test2.com', 124)
        self.test_results.record_total_difficulty('test3.com', 125)
        self.assertEqual(self.test_results.get_highest_total_difficulty(), 125)

    def test_write_metrics(self):
        metrics = MagicMock()
    
        self.test_results.record_health('test1.com', True)
        self.test_results.record_head_count('test2.com', 123)
        self.test_results.record_disconnects('test3.com', 100)
        self.test_results.record_latency('test1.com', 1.23)
        self.test_results.record_block_height('test2.com', 123)
        self.test_results.record_total_difficulty('test1.com', 123)
        self.test_results.record_difficulty('test3.com', 123)
        self.test_results.record_gas_price('test1.com', 1.23)
        self.test_results.record_max_priority_fee('test2.com', 1.123)
        self.test_results.record_client_version('test1.com', 'ClientVersion123')

        self.test_results.write_metrics(metrics)

        calls = [
            call.__getitem__('brpc_health'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], True),
            call.__getitem__('brpc_latency'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 1.23),
            call.__getitem__('brpc_total_difficulty'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 123),
            call.__getitem__('brpc_difficulty_behind_highest'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 0),
            call.__getitem__('brpc_gas_price'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 1.23),
            call.__getitem__('brpc_client_version'),
            call.__getitem__().add_metric(
                ['test1.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'],
                value={'client_version': 'ClientVersion123'}),
            call.__getitem__('brpc_head_count'),
            call.__getitem__().add_metric(
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 123),
            call.__getitem__('brpc_block_height'),
            call.__getitem__().add_metric(
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 123),
            call.__getitem__('brpc_block_height_behind_highest'),
            call.__getitem__().add_metric(
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 0),
            call.__getitem__('brpc_max_priority_fee'),
            call.__getitem__().add_metric(
                ['test2.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 1.123),
            call.__getitem__('brpc_disconnects'),
            call.__getitem__().add_metric(
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 100),
            call.__getitem__('brpc_difficulty'),
            call.__getitem__().add_metric(
                ['test3.com', 'test_provider', 'test_blockchain', 'test_network_name', 'test_network_type'], 123)
        ]
        # Validate that proper calls were made
        metrics.assert_has_calls(calls)
        # Validate that metadata was cleared after the write_metrics
        self.assertEqual(self.test_results.metadata, {})
        
if __name__ == '__main__':
    unittest.main()

