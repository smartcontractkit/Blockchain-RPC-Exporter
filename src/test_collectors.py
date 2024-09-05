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


class TestConfluxCollector(TestCase):
    """Tests the conflux collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.client_params = {"param1": "dummy", "param2": "data"}
        self.sub_payload = {
            "method": 'cfx_subscribe',
            "jsonrpc": "2.0",
            "id": self.chain_id,
            "params": ["newHeads"]
        }
        with mock.patch('collectors.WebsocketInterface') as mocked_websocket:
            self.conflux_collector = collectors.ConfluxCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_websocket = mocked_websocket

    def test_websocket_interface_created(self):
        """Tests that the conflux collector calls the websocket interface with the correct args"""
        self.mocked_websocket.assert_called_once_with(
            self.url, self.sub_payload, **self.client_params)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.conflux_collector, 'interface'))

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
        self.assertTrue(self.conflux_collector.alive())

    def test_alive_is_false(self):
        """Tests the alive function returns false when websocket.healthy is false"""
        self.mocked_websocket.return_value.healthy = False
        self.assertFalse(self.conflux_collector.alive())

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.conflux_collector.block_height()
        self.mocked_websocket.return_value.get_message_property_to_hex.assert_called_once_with(
            'height')

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        payload = {
            "jsonrpc": "2.0",
            "method": "cfx_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        self.conflux_collector.client_version()
        self.mocked_websocket.return_value.cached_query.assert_called_once_with(
            payload)

    def test_client_version_return_none(self):
        """Tests that the client_version returns None if the query returns no version"""
        self.mocked_websocket.return_value.cached_query.return_value = None
        result = self.conflux_collector.client_version()
        self.assertEqual(None, result)

    def test_client_version_return(self):
        """Tests that the client_version is returned in the correct format"""
        self.mocked_websocket.return_value.cached_query.return_value = "test/v1.23"
        result = self.conflux_collector.client_version()
        self.assertEqual({"client_version": "test/v1.23"}, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on subscription ping"""
        self.mocked_websocket.return_value.subscription_ping_latency = 0.123
        self.assertEqual(0.123, self.conflux_collector.latency())


class TestCardanoCollector(TestCase):
    """Tests the cardano collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.client_params = {"param1": "dummy", "param2": "data"}
        self.block_height_payload = {
            "id": "exporter",
            "jsonrpc": "2.0",
            "method": "queryNetwork/blockHeight"
        }
        with mock.patch('collectors.WebsocketInterface') as mocked_websocket:
            self.cardano_collector = collectors.CardanoCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_websocket = mocked_websocket

    def test_websocket_interface_created(self):
        """Tests that the cardano collector calls the websocket interface with the correct args"""
        self.mocked_websocket.assert_called_once_with(
            self.url, **self.client_params)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.cardano_collector, 'interface'))

    def test_websocket_attr_daemon_is_none(self):
        """Tests that the daemon attribute is None"""
        self.assertEqual(None, self.mocked_websocket.return_value.daemon)

    def test_alive_call(self):
        """Tests the alive function uses the correct call and args"""
        self.cardano_collector.alive()
        self.mocked_websocket.return_value.cached_query.assert_called_once_with(
            self.block_height_payload, skip_checks=True)

    def test_alive_false(self):
        """Tests the alive function returns false when query returns None"""
        self.mocked_websocket.return_value.cached_query.return_value = None
        result = self.cardano_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.cardano_collector.block_height()
        self.mocked_websocket.return_value.cached_query.assert_called_once_with(
            self.block_height_payload, skip_checks=True)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_websocket.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.cardano_collector.latency())


class TestBitcoinCollector(TestCase):
    """Tests the bitcoin collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        self.network_info_payload = {
            "jsonrpc": "1.0",
            "id": "exporter",
            "method": "getnetworkinfo"
        }
        self.blockchain_info_payload = {
            "jsonrpc": "1.0",
            "id": "exporter",
            "method": "getblockchaininfo",
            "params": []
        }
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.bitcoin_collector = collectors.BitcoinCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {
            'component': 'BitcoinCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.bitcoin_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the bitcoin collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.bitcoin_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call and args"""
        self.bitcoin_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.network_info_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.bitcoin_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.bitcoin_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.blockchain_info_payload)

    def test_block_height_get_blocks_key(self):
        """Tests that the block height is returned with the blocks key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "blocks": 5}
        result = self.bitcoin_collector.block_height()
        self.assertEqual(5, result)

    def test_block_height_key_error_returns_none(self):
        """Tests that the block height returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.bitcoin_collector.block_height()
        self.assertEqual(None, result)

    def test_block_height_returns_none(self):
        """Tests that the block height returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.bitcoin_collector.block_height()
        self.assertEqual(None, result)

    def test_total_difficulty(self):
        """Tests the total_difficulty function uses the correct call and args to get difficulty"""
        self.bitcoin_collector.total_difficulty()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.blockchain_info_payload)

    def test_total_difficulty_get_blocks_key(self):
        """Tests that the difficulty is returned with the difficulty key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "difficulty": 5}
        result = self.bitcoin_collector.total_difficulty()
        self.assertEqual(5, result)

    def test_total_difficulty_key_error_returns_none(self):
        """Tests that the total_difficulty returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.bitcoin_collector.total_difficulty()
        self.assertEqual(None, result)

    def test_total_difficulty_returns_none(self):
        """Tests that the total_difficulty returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.bitcoin_collector.total_difficulty()
        self.assertEqual(None, result)

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        self.bitcoin_collector.client_version()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.network_info_payload)

    def test_client_version_get_blocks_key(self):
        """Tests that the client version is returned as a string with the version key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "version": 5, "subversion": 6, "protocolversion": 7}
        result = self.bitcoin_collector.client_version()
        self.assertEqual(
            {"client_version": "version:5 subversion:6 protocolversion:7"}, result)

    def test_client_version_key_error_returns_none(self):
        """Tests that the client_version returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.bitcoin_collector.client_version()
        self.assertEqual(None, result)

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.bitcoin_collector.client_version()
        self.assertEqual(None, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.bitcoin_collector.latency())


class TestFilecoinCollector(TestCase):
    """Tests the filecoin collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        self.client_version_payload = {
            'jsonrpc': '2.0',
            'method': "Filecoin.Version",
            'id': 1
        }
        self.block_height_payload = {
            'jsonrpc': '2.0',
            'method': "Filecoin.ChainHead",
            'id': 1
        }
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.filecoin_collector = collectors.FilecoinCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {
            'component': 'FilecoinCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.filecoin_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the filecoin collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.filecoin_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call and args"""
        self.filecoin_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.client_version_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.filecoin_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.filecoin_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.block_height_payload)

    def test_block_height_get_blocks_key(self):
        """Tests that the block height is returned with the Height key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "Height": 5}
        result = self.filecoin_collector.block_height()
        self.assertEqual(5, result)

    def test_block_height_key_error_returns_none(self):
        """Tests that the block height returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.filecoin_collector.block_height()
        self.assertEqual(None, result)

    def test_block_height_returns_none(self):
        """Tests that the block height returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.filecoin_collector.block_height()
        self.assertEqual(None, result)

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        self.filecoin_collector.client_version()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.client_version_payload)

    def test_client_version_get_blocks_key(self):
        """Tests that the client version is returned as a string with the version key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "Version": 5, "APIVersion": 6}
        result = self.filecoin_collector.client_version()
        self.assertEqual({"client_version": "version:5 APIversion:6"}, result)

    def test_client_version_key_error_returns_none(self):
        """Tests that the client_version returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.filecoin_collector.client_version()
        self.assertEqual(None, result)

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.filecoin_collector.client_version()
        self.assertEqual(None, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.filecoin_collector.latency())


class TestSolanaCollector(TestCase):
    """Tests the solana collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        self.client_version_payload = {
            'jsonrpc': '2.0',
            'method': "getVersion",
            'id': 1
        }
        self.block_height_payload = {
            'jsonrpc': '2.0',
            'method': "getBlockHeight",
            'id': 1
        }
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.solana_collector = collectors.SolanaCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url
        function."""
        expected_metadata = {
            'component': 'SolanaCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.solana_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the solana collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.solana_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call and args"""
        self.solana_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.client_version_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.solana_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.solana_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.block_height_payload)

    def test_block_height_returns_none(self):
        """Tests that the block height returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.solana_collector.block_height()
        self.assertEqual(None, result)

    def test_client_version(self):
        """Tests the client_version function uses the correct call and args to get client version"""
        self.solana_collector.client_version()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.client_version_payload)

    def test_client_version_get_blocks_key(self):
        """Tests that the client version is returned as a string with the solana-core key"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "solana-core": 5}
        result = self.solana_collector.client_version()
        self.assertEqual({"client_version": "5"}, result)

    def test_client_version_key_error_returns_none(self):
        """Tests that the client_version returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = {
            "dummy_key": 5}
        result = self.solana_collector.client_version()
        self.assertEqual(None, result)

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.solana_collector.client_version()
        self.assertEqual(None, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.solana_collector.latency())


class TestStarknetCollector(TestCase):
    """Tests the starknet collector class"""

    def setUp(self):
        self.url = "wss://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        self.block_height_payload = {
            "method": "starknet_blockNumber",
            "jsonrpc": "2.0",
            "id": 1
        }
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.starknet_collector = collectors.StarknetCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_https_interface_created(self):
        """Tests that the starknet collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists.
        May be used by external calls to access objects such as the interface cache"""
        self.assertTrue(hasattr(self.starknet_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call and args"""
        self.starknet_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.block_height_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.starknet_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call and args to get block height"""
        self.starknet_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.block_height_payload)

    def test_block_height_returns_none(self):
        """Tests that the block height returns None if json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.starknet_collector.block_height()
        self.assertEqual(None, result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.starknet_collector.latency())

class TestAptosCollector(TestCase):
    """Tests the Aptos collector class"""

    def setUp(self):
        self.url = "https://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.aptos_collector = collectors.AptosCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url function."""
        expected_metadata = {
            'component': 'AptosCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.aptos_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the Aptos collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists."""
        self.assertTrue(hasattr(self.aptos_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call"""
        self.aptos_collector.alive()
        self.mocked_connection.return_value.cached_json_rest_api_get.assert_called_once()

    def test_alive_false(self):
        """Tests the alive function returns false when get returns None"""
        self.mocked_connection.return_value.cached_json_rest_api_get.return_value = None
        result = self.aptos_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call to get block height"""
        self.aptos_collector.block_height()
        self.mocked_connection.return_value.cached_json_rest_api_get.assert_called_once()

    def test_block_height_returns_none(self):
        """Tests that the block height returns None if cached_json_rest_api_get returns None"""
        self.mocked_connection.return_value.cached_json_rest_api_get.return_value = None
        result = self.aptos_collector.block_height()
        self.assertIsNone(result)

    def test_client_version(self):
        """Tests the client_version function uses the correct call to get client version"""
        self.aptos_collector.client_version()
        self.mocked_connection.return_value.cached_json_rest_api_get.assert_called_once()

    def test_client_version_get_git_hash(self):
        """Tests that the client version is returned as a string with the git_hash key"""
        self.mocked_connection.return_value.cached_json_rest_api_get.return_value = {
            "git_hash": "abcdef123"}
        result = self.aptos_collector.client_version()
        self.assertEqual({"client_version": "abcdef123"}, result)

    def test_client_version_key_error_returns_none(self):
        """Tests that the client_version returns None on KeyError"""
        self.mocked_connection.return_value.cached_json_rest_api_get.return_value = {
            "dummy_key": "value"}
        result = self.aptos_collector.client_version()
        self.assertIsNone(result)

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if cached_json_rest_api_get returns None"""
        self.mocked_connection.return_value.cached_json_rest_api_get.return_value = None
        result = self.aptos_collector.client_version()
        self.assertIsNone(result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.aptos_collector.latency())

class TestTronCollector(TestCase):
    """Tests the Tron collector class"""

    def setUp(self):
        self.url = "https://test.com"
        self.labels = ["dummy", "labels"]
        self.chain_id = 123
        self.open_timeout = 8
        self.ping_timeout = 9
        self.client_params = {
            "open_timeout": self.open_timeout, "ping_timeout": self.ping_timeout}
        with mock.patch('collectors.HttpsInterface') as mocked_connection:
            self.tron_collector = collectors.TronCollector(
                self.url, self.labels, self.chain_id, **self.client_params)
            self.mocked_connection = mocked_connection

    def test_logger_metadata(self):
        """Validate logger metadata. Makes sure url is stripped by helpers.strip_url function."""
        expected_metadata = {
            'component': 'TronCollector', 'url': 'test.com'}
        self.assertEqual(expected_metadata,
                         self.tron_collector._logger_metadata)

    def test_https_interface_created(self):
        """Tests that the Tron collector calls the https interface with the correct args"""
        self.mocked_connection.assert_called_once_with(
            self.url, self.open_timeout, self.ping_timeout)

    def test_interface_attribute_exists(self):
        """Tests that the interface attribute exists."""
        self.assertTrue(hasattr(self.tron_collector, 'interface'))

    def test_alive_call(self):
        """Tests the alive function uses the correct call"""
        self.tron_collector.alive()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.tron_collector.client_version_payload)

    def test_alive_false(self):
        """Tests the alive function returns false when post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.tron_collector.alive()
        self.assertFalse(result)

    def test_block_height(self):
        """Tests the block_height function uses the correct call to get block height"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = "0x1a2b3c"
        result = self.tron_collector.block_height()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.tron_collector.block_height_payload)
        self.assertEqual(result, 1715004)

    def test_block_height_raises_value_error(self):
        """Tests that the block height raises ValueError if result is invalid"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = "invalid"
        with self.assertRaises(ValueError):
            self.tron_collector.block_height()

    def test_client_version(self):
        """Tests the client_version function uses the correct call to get client version"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = "Tron/v1.0.0"
        result = self.tron_collector.client_version()
        self.mocked_connection.return_value.cached_json_rpc_post.assert_called_once_with(
            self.tron_collector.client_version_payload)
        self.assertEqual(result, {"client_version": "Tron/v1.0.0"})

    def test_client_version_returns_none(self):
        """Tests that the client_version returns None if cached_json_rpc_post returns None"""
        self.mocked_connection.return_value.cached_json_rpc_post.return_value = None
        result = self.tron_collector.client_version()
        self.assertIsNone(result)

    def test_latency(self):
        """Tests that the latency is obtained from the interface based on latest_query_latency"""
        self.mocked_connection.return_value.latest_query_latency = 0.123
        self.assertEqual(0.123, self.tron_collector.latency())
