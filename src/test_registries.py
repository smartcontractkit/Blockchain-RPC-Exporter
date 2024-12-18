"""Tests the registries module"""
import os
from unittest import TestCase, mock
from structlog.testing import capture_logs


from registries import Endpoint, EndpointRegistry, CollectorRegistry


class TestEndpoint(TestCase):  # pylint: disable=too-many-instance-attributes
    """Tests the Endpoint class"""

    def setUp(self):
        """Creates dummy data for a test endpoint"""
        self.url = "http://test.com"
        self.provider = "provider"
        self.blockchain = "test_chain"
        self.network_name = "test_network"
        self.network_type = "ETH"
        self.integration_maturity = "development"
        self.canonical_name = "test-chain-network"
        self.chain_selector = 121212
        self.chain_id = 123
        self.client_params = {"dummy": "data"}
        self.endpoint = Endpoint(self.url, self.provider, self.blockchain,
                                 self.network_name, self.network_type,
                                 self.integration_maturity, self.canonical_name,
                                 self.chain_selector,
                                 self.chain_id, **self.client_params)

    def test_url_attribute(self):
        """Tests the url attribute is set correctly"""
        self.assertEqual(self.url, self.endpoint.url)

    def test_chain_id_attribute(self):
        """Tests the chain_id attribute is set correctly"""
        self.assertEqual(self.chain_id, self.endpoint.chain_id)

    def test_labels_attribute(self):
        """Tests the labels attribute is set correctly"""
        labels = [self.url, self.provider, self.blockchain,
                  self.network_name, self.network_type,
                  self.integration_maturity, self.canonical_name,
                  str(self.chain_selector),
                  str(self.chain_id)]
        self.assertEqual(labels, self.endpoint.labels)


class TestEndpointRegistry(TestCase):
    """Tests the EndpointRegistry class"""
    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_bitcoin.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def setUp(self):
        self.endpoint_registry = EndpointRegistry()

    def test_logger_metadata(self):
        """Tests that the logger metadata is correct"""
        expected_metadata = {'component': 'Registries'}
        self.assertDictEqual(
            expected_metadata,
            self.endpoint_registry._logger_metadata)  # pylint: disable=protected-access

    def test_blockchain_property(self):
        """Tests the blockchain property returns the correct value"""
        self.assertEqual('bitcoin', self.endpoint_registry.blockchain)

    def test_collector_property(self):
        """Tests the collector property returns the correct value"""
        self.assertEqual('bitcoin', self.endpoint_registry.collector)


class TestCollectorRegistry(TestCase):
    """Tests the CollectorRegistry class"""

    def setUp(self):
        self.collector_registry = None

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_conflux.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_conflux(self):
        """Tests that the conflux collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.ConfluxCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_cardano.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_cardano(self):
        """Tests that the cardano collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.CardanoCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_bitcoin.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_bitcoin(self):
        """Tests that the bitcoin collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.BitcoinCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_filecoin.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_filecoin(self):
        """Tests that the filecoin collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.FilecoinCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_solana.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_solana(self):
        """Tests that the solana collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.SolanaCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_starknet.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_starknet(self):
        """Tests that the starknet collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.StarknetCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_aptos.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_aptos(self):
        """Tests that the aptos collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.AptosCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_tron.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_tron(self):
        """Tests that the Tron collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.TronCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_evmhttp.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_evmhttp(self):
        """Tests that the EVM HTTP collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.EvmHttpCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_evm.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_evm(self):
        """Tests that the evm collector is called with the correct args"""
        self.collector_registry = CollectorRegistry()
        with mock.patch('collectors.EvmCollector', new=mock.Mock()) as collector:
            helper_test_collector_registry(self, collector)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_unsupported_blockchain.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_unsupported_chain_exit(self):
        """Tests that the program exits when loading a config file with an unsupported chain"""
        with self.assertRaises(SystemExit) as raises_context:
            self.collector_registry = CollectorRegistry()
            self.collector_registry.get_collector_registry  # pylint: disable=pointless-statement
        self.assertEqual(1, raises_context.exception.code)

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_unsupported_blockchain.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_for_unsupported_chain_error_log(self):
        """Tests that an error is logged when loading a config file with an unsupported chain"""
        try:
            with capture_logs() as captured:
                self.collector_registry = CollectorRegistry()
                self.collector_registry.get_collector_registry  # pylint: disable=pointless-statement
        except SystemExit:
            # Catch and pass on expected SystemExit so tests keep running
            pass
        self.assertTrue(any(
            log['log_level'] == "error" for log in captured))  # pylint: disable=duplicate-code

    @mock.patch.dict(os.environ, {
        "CONFIG_FILE_PATH": "tests/fixtures/configuration_bitcoin.yaml",
        "VALIDATION_FILE_PATH": "tests/fixtures/validation.yaml"
    })
    def test_get_collector_registry_no_error_log(self):
        """Tests that no error is logged when loading a valid config file"""
        try:
            with capture_logs() as captured:
                self.collector_registry = CollectorRegistry()
                self.collector_registry.get_collector_registry  # pylint: disable=pointless-statement
        except SystemExit:
            # Catch and pass on expected SystemExit so tests keep running
            pass
        self.assertFalse(
            any(log['log_level'] == "error" for log in captured))


def helper_test_collector_registry(test_collector_registry, mock_collector):
    """Helper function to check the collector list calls the mock and
    ensure the called collector uses the correct args.
    This function is to avoid duplicating the code for each collector type"""
    collector_list = test_collector_registry.collector_registry.get_collector_registry
    test_collector_registry.assertTrue(
        all(isinstance(col, mock.Mock) for col in collector_list))
    calls = []
    for item in test_collector_registry.collector_registry.get_endpoint_registry:
        calls.append(mock.call(item.url, item.labels, item.chain_id,
                     **test_collector_registry.collector_registry.client_parameters))
    mock_collector.assert_has_calls(calls, False)
