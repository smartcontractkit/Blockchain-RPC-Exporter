# pylint: disable=protected-access,invalid-name
"""Module for testing Config"""

import os
from unittest import TestCase, mock
from structlog.testing import capture_logs

from configuration import Config

CONFIG_FILES = {"valid": "tests/fixtures/configuration.yaml",
                "invalid": "tests/fixtures/configuration_invalid.yaml",
                "client_params": "tests/fixtures/configuration_conn_params.yaml"}
VALIDATION_FILE = {"valid": "tests/fixtures/validation.yaml"}


class TestConfiguration(TestCase):
    """Tests all configuration.Config attributes used externally."""

    def setUp(self):
        """Set up dummy configs for us."""
        self.maxDiff = None
        self.config = setup_config_object(
            CONFIG_FILES["valid"], VALIDATION_FILE["valid"])
        self.client_params_config = setup_config_object(
            CONFIG_FILES["client_params"], VALIDATION_FILE["valid"])
        self.invalid_config = setup_config_object(
            CONFIG_FILES["invalid"], VALIDATION_FILE["valid"])

    def test_invalid_get_property(self):
        """Tests getting invalid properties returns None type"""
        config_property = self.config.get_property('invalid')
        self.assertEqual(config_property, None)

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

    def test_client_parameters_attribute_present(self):
        """Make sure we use explicitly provided client parameters in the config if
        they are set."""
        expected = {
            'open_timeout': 1,
            'close_timeout': 2,
            'ping_interval': 3,
            'ping_timeout': 4
        }
        self.assertDictEqual(
            self.client_params_config.client_parameters, expected)

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

    def test_load_and_validate_schema_exception_exit(self):
        """Tests that the program exits when loading a configuration file with a schema exception"""
        with self.assertRaises(SystemExit) as cm:
            self.invalid_config._configuration
        self.assertEqual(1, cm.exception.code)

    def test_load_and_validate_schema_execption_error_log(self):
        """Tests that an error is logged when loading a config file with a schema exception"""
        try:
            with capture_logs() as captured:
                self.invalid_config._configuration
        except SystemExit:
            pass
        self.assertEqual("error", captured[0]['log_level'])


def setup_config_object(config_file, validation_file) -> Config:
    """Creates a Config object using the provided config and validation files"""
    with mock.patch.dict(
            os.environ, {
                "CONFIG_FILE_PATH": config_file,
                "VALIDATION_FILE_PATH": validation_file
            }):
        return Config()
