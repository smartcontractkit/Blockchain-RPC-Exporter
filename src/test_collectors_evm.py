# pylint: disable=protected-access, too-many-instance-attributes, duplicate-code
"""Module for testing collectors"""
from unittest import TestCase, mock

import collectors


class TestEvmCollector(TestCase):
    """Tests the evm collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.client_params = {"param1": "dummy", "param2": "data"}
        self.sub_payload = {
            "method": 'eth_subscribe',
            "jsonrpc": "2.0",
            "id": self.chain_id,
            "params": ["newHeads"]
        }
        with mock.patch('collectors.WebsocketInterface') as mocked_websocket:
            self.evm_collector = collectors.EvmCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_websocket = mocked_websocket

    def test_websocket_interface_created(self):
        """Tests that the evm collector calls the websocket interface with the correct args"""
        self.mocked_websocket.assert_called_once_with(
            self.url, self.sub_payload, **self.client_params)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.evm_collector, 'interface'))

    def test_websocket_attr_daemon_is_bool(self):
        """Tests that the daemon attribute is of type bool"""
        self.assertEqual(bool, type(self.mocked_websocket.return_value.daemon))

    def test_websocket_daemon_true(self):
        """Tests that the websocket object has daemon set to true"""
        self.assertTrue(self.mocked_websocket.return_value.daemon)

    def test_websocket_start_called(self):
        """Tests that the websocket object start function is called"""
        self.mocked_websocket.return_value.start.assert_called_once_with()

    def test_alive_is_true(self):
        """Tests the alive function returns true when websocket.healthy is true"""
        self.mocked_websocket.return_value.healthy = True
        self.assertTrue(self.evm_collector.alive())

    def test_alive_is_false(self):
        """Tests the alive function returns false when websocket.healthy is false"""
        self.mocked_websocket.return_value.healthy = False
        self.assertFalse(self.evm_collector.alive())

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.evm_collector.block_height()
        self.mocked_websocket.return_value.get_message_property_to_hex.assert_called_once_with(
            'number')

    def test_finalized_block_height(self):
        """Tests that finalized_block_height uses correct call and args to get finalized block"""
        # Mock with hex string, not integer
        mock_block_response = {"number": "0x1a2b3c"}
        self.mocked_websocket.return_value.query.return_value = mock_block_response

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": ["finalized", False],
            "id": self.chain_id
        }
        self.evm_collector.finalized_block_height()
        self.mocked_websocket.return_value.query.assert_called_once_with(payload)

    def test_finalized_block_height_return_none_when_query_none(self):
        """Tests that finalized_block_height returns None if the query returns None"""
        self.mocked_websocket.return_value.query.return_value = None
        result = self.evm_collector.finalized_block_height()
        self.assertEqual(None, result)

    def test_finalized_block_height_return_none_when_no_number_field(self):
        """Tests that finalized_block_height returns None if the response has no 'number' field"""
        self.mocked_websocket.return_value.query.return_value = {"hash": "0x123"}
        result = self.evm_collector.finalized_block_height()
        self.assertEqual(None, result)

    def test_finalized_block_height_return(self):
        """Tests that finalized_block_height converts hex block number to integer correctly"""
        mock_block_response = {
            "number": "0x1a2b3c",  # Hex string as your code expects
            "hash": "0x456def"
        }
        self.mocked_websocket.return_value.query.return_value = mock_block_response
        result = self.evm_collector.finalized_block_height()
        # 0x1a2b3c = 1715004 in decimal
        self.assertEqual(1715004, result)

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        payload = {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        self.evm_collector.client_version()
        self.mocked_websocket.return_value.cached_query.assert_called_once_with(
            payload)

    def test_client_version_return_none(self):
        """Tests that the client_version returns None if the query returns no version"""
        self.mocked_websocket.return_value.cached_query.return_value = None
        result = self.evm_collector.client_version()
        self.assertEqual(None, result)

    def test_client_version_return(self):
        """Tests that the client_version is returned in the correct format"""
        self.mocked_websocket.return_value.cached_query.return_value = "test/v1.23"
        result = self.evm_collector.client_version()
        self.assertEqual({"client_version": "test/v1.23"}, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on subscription ping"""
        self.mocked_websocket.return_value.subscription_ping_latency = 0.123
        self.assertEqual(0.123, self.evm_collector.latency())

class TestEvmHttpCollector(TestCase):
    """Tests the EvmHttp collector class"""

    def setUp(self):
        self.url = "https://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.evmhttp_collector = collectors.EvmHttpCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url function."""
        expected_metadata = {
            'component': 'EvmHttpCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.evmhttp_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the EvmHttp collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists."""
        self.assertTrue(hasattr(self.evmhttp_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call"""
        self.evmhttp_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.evmhttp_collector.client_version_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.evmhttp_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call to get block height"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = "0x1a2b3c"
        result = self.evmhttp_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.evmhttp_collector.block_height_payload)
        self.assertEqual(result, 1715004)

    def test_block_height_raises_value_error(self):
        """Tests that the block height raises ValueError if result is invalid"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = "invalid"
        with self.assertRaises(ValueError):
            self.evmhttp_collector.block_height()

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        payload = {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "id": 1
        }
        self.evmhttp_collector.client_version()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            payload)

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if cached_json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.evmhttp_collector.client_version()
        self.assertIsNone(result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.evmhttp_collector.latency())
