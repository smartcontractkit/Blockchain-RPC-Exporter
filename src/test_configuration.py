#pylint: disable=protected-access,invalid-name

"""Module for testing Config"""

import os
from unittest import TestCase, mock
from configuration import Config


class TestConfiguration(TestCase):
    """Tests all configuration.Config attributes used externally."""

    @mock.patch.dict(
        os.environ, {
            "CONFIG_FILE_PATH": "tests/fixtures/configuration.yaml",
            "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
        })
    def setUp(self):
        """Set up dummy config for us."""
        self.maxDiff = None
        self.config = Config()

    def test_configuration_attribute(self):
        """Make sure that the configuration is what we expect after loading."""
        expected_configuration = {
            "blockchain":
            "TestChain",
            "chain_id":
            1234,
            "network_name":
            "TestNetwork",
            "network_type":
            "Mainnet",
            "collector":
            "evm",
            "endpoints": [{
                "url": "wss://test1.com",
                "provider": "TestProvider1"
            }, {
                "url": "wss://test2.com",
                "provider": "TestProvider2"
            }, {
                "url": "wss://test3.com",
                "provider": "TestProvider3"
            }]
        }
        self.assertEqual(expected_configuration, self.config._configuration)

    def test_client_parameters_attribute_not_present(self):
        """Make sure that we have defaults on client_parameters if they are not
        explicitly set in the configuration."""
        expected = {
            'open_timeout': 7,
            'close_timeout': 3,
            'ping_interval': 10,
            'ping_timeout': 7
        }
        self.assertEqual(self.config.client_parameters, expected)

    @mock.patch.dict(
        os.environ, {
            "CONFIG_FILE_PATH":
            "tests/fixtures/configuration_conn_params.yaml",
            "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
        })
    def test_client_parameters_attribute_present(self):
        """Make sure we use explicitly provided client parameters in the config if
        they are set."""
        cfg = Config()
        expected = {
            'open_timeout': 1,
            'close_timeout': 2,
            'ping_interval': 3,
            'ping_timeout': 4
        }
        self.assertEqual(cfg.client_parameters, expected)

    def test_endpoints_attribute(self):
        """Make sure we parsed endpoints correctly as expected by external
        parent classes."""
        expected = [{
            'url': 'wss://test1.com',
            'provider': 'TestProvider1'
        }, {
            'provider': 'TestProvider2',
            'url': 'wss://test2.com'
        }, {
            'provider': 'TestProvider3',
            'url': 'wss://test3.com'
        }]
        self.assertEqual(expected, self.config.endpoints)
