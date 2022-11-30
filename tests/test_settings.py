import unittest
from unittest.mock import MagicMock, call, patch, mock_open
from unittest import mock
from src.settings import configuration, logger


class test_configuration(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.configuration = configuration("tests/fixtures/test_configuration.yaml",
                                           "tests/fixtures/test_validation.yaml")

    def test_allowed_providers_attr(self):
        expected_allowed_providers = ['TestProvider1', 'TestProvider2', 'TestProvider3']
        self.assertEqual(self.configuration.allowed_providers, expected_allowed_providers)

    def test_configuration_attr(self):
        expected_post_process_configuration = {
            'blockchain':
            'Ethereum',
            'chain_id':
            1,
            'network_name':
            'Mainnet',
            'network_type':
            'Mainnet',
            'collector':
            'evm',
            'endpoints': [{
                'url': 'wss://test1.com',
                'provider': 'TestProvider1',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }, {
                'url': 'wss://test2.com',
                'provider': 'TestProvider2',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }, {
                'url': 'wss://test3.com',
                'provider': 'TestProvider3',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }]
        }
        self.assertEqual(expected_post_process_configuration, self.configuration.configuration)

    def test_blockchain_attr(self):
        self.assertEqual(self.configuration.blockchain, 'Ethereum')

    def test_populate_endpoints_metadata(self):
        self.configuration._add_metadata_to_all_endpoints = MagicMock(return_value=None)
        self.configuration._populate_endpoints_metadata()
        calls = [call('blockchain', 'Ethereum'), call('network_type', 'Mainnet'), call('network_name', 'Mainnet')]
        self.configuration._add_metadata_to_all_endpoints.assert_has_calls(calls)

    def test_add_metadata_to_all_endpoints(self):
        self.configuration._add_metadata_to_all_endpoints('test_key', 'test_value')
        expected_configuration = {
            'blockchain':
            'Ethereum',
            'chain_id':
            1,
            'network_name':
            'Mainnet',
            'network_type':
            'Mainnet',
            'collector':
            'evm',
            'endpoints': [{
                'url': 'wss://test1.com',
                'provider': 'TestProvider1',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1,
                'test_key': 'test_value'
            }, {
                'url': 'wss://test2.com',
                'provider': 'TestProvider2',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1,
                'test_key': 'test_value'
            }, {
                'url': 'wss://test3.com',
                'provider': 'TestProvider3',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1,
                'test_key': 'test_value'
            }]
        }
        self.assertEqual(self.configuration.configuration, expected_configuration)

    def test_endpoints_attr(self):
        expected_endpoints = [{
            'url': 'wss://test1.com',
            'provider': 'TestProvider1',
            'blockchain': 'Ethereum',
            'network_type': 'Mainnet',
            'network_name': 'Mainnet',
            'chain_id': 1
        }, {
            'url': 'wss://test2.com',
            'provider': 'TestProvider2',
            'blockchain': 'Ethereum',
            'network_type': 'Mainnet',
            'network_name': 'Mainnet',
            'chain_id': 1
        }, {
            'url': 'wss://test3.com',
            'provider': 'TestProvider3',
            'blockchain': 'Ethereum',
            'network_type': 'Mainnet',
            'network_name': 'Mainnet',
            'chain_id': 1
        }]
        self.assertEqual(self.configuration.endpoints, expected_endpoints)

    def test_isEvm_attr_evm(self):
        self.assertEqual(self.configuration.isEvm(), True)
        self.assertEqual(self.configuration.isSolana(), False)
        self.assertEqual(self.configuration.isCardano(), False)
        self.assertEqual(self.configuration.isConflux(), False)
        self.assertEqual(self.configuration.isBitcoin(), False)
        self.assertEqual(self.configuration.isDoge(), False)
        self.assertEqual(self.configuration.isFilecoin(), False)
        self.assertEqual(self.configuration.isStarkware(), False)

    def test_isEvm_attr_notEvm(self):
        config = {
            'blockchain':
            'Conflux',
            'chain_id':
            1,
            'network_name':
            'Mainnet',
            'network_type':
            'Mainnet',
            'collector':
            'conflux',
            'endpoints': [{
                'url': 'wss://test1.com',
                'provider': 'TestProvider1',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }, {
                'url': 'wss://test2.com',
                'provider': 'TestProvider2',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }, {
                'url': 'wss://test3.com',
                'provider': 'TestProvider3',
                'blockchain': 'Ethereum',
                'network_type': 'Mainnet',
                'network_name': 'Mainnet',
                'chain_id': 1
            }]
        }
        with patch.object(configuration, '_load_configuration_file', return_value=config):
            cfg = configuration("tests/fixtures/test_configuration.yaml", "tests/fixtures/test_validation.yaml")

            self.assertEqual(cfg.isEvm(), False)
            self.assertEqual(cfg.isSolana(), False)
            self.assertEqual(cfg.isCardano(), False)
            self.assertEqual(cfg.isConflux(), True)
            self.assertEqual(cfg.isBitcoin(), False)
            self.assertEqual(cfg.isDoge(), False)
            self.assertEqual(cfg.isFilecoin(), False)
            self.assertEqual(cfg.isStarkware(), False)

    def test_wrong_configuration_file_path(self):
        with self.assertRaises(SystemExit):
            cfg = configuration("tests/fixtures/wrong_path.yaml", "tests/fixtures/test_validation.yaml")

    def test_wrong_validation_file_path(self):
        with self.assertRaises(SystemExit):
            cfg = configuration("tests/fixtures/wrong_path.yaml", "tests/fixtures/test_validation.yaml")

    def test_broken_config_schema(self):
        with self.assertRaises(SystemExit):
            cfg = configuration("tests/fixtures/test_configuration.yaml", "tests/fixtures/wrong_path.yaml")

    def test_broken_validation_schema(self):
        with self.assertRaises(SystemExit):
            cfg = configuration("tests/fixtures/test_configuration.yaml", "tests/fixtures/test_validation_broken.yaml")


if __name__ == '__main__':
    unittest.main()
