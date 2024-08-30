"""Module for providing interfaces to interact with https and websocket RPC endpoints."""
from interfaces import WebsocketInterface, HttpsInterface
from helpers import validate_dict_and_return_key_value, strip_url

class EvmCollector():
    """A collector to fetch information about evm compatible RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id

        sub_payload = {
            "method": 'eth_subscribe',
            "jsonrpc": "2.0",
            "id": chain_id,
            "params": ["newHeads"]
        }
        self.interface = WebsocketInterface(
            url, sub_payload, **client_parameters)
        self.interface.daemon = True
        self.interface.start()

    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.interface.healthy

    def block_height(self):
        """Returns latest block height."""
        return self.interface.get_message_property_to_hex('number')

    def heads_received(self):
        """Returns amount of received messages from the subscription."""
        return self.interface.heads_received

    def disconnects(self):
        """Returns number of disconnects on the subscription."""
        return self.interface.disconnects

    def latency(self):
        """Returns connection latency."""
        return self.interface.subscription_ping_latency

    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        version = self.interface.cached_query(payload)
        if version is None:
            return None
        client_version = {"client_version": version}
        return client_version


class ConfluxCollector():
    """A collector to fetch information about conflux RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id

        sub_payload = {
            "method": 'cfx_subscribe',
            "jsonrpc": "2.0",
            "id": chain_id,
            "params": ["newHeads"]
        }
        self.interface = WebsocketInterface(
            url, sub_payload, **client_parameters)
        self.interface.daemon = True
        self.interface.start()

    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.interface.healthy

    def block_height(self):
        """Returns latest block height."""
        return self.interface.get_message_property_to_hex('height')

    def heads_received(self):
        """Returns amount of received messages from the subscription."""
        return self.interface.heads_received

    def disconnects(self):
        """Returns number of disconnects on the subscription."""
        return self.interface.disconnects

    def latency(self):
        """Returns connection latency."""
        return self.interface.subscription_ping_latency

    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "cfx_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        version = self.interface.cached_query(payload)
        if version is None:
            return None
        client_version = {"client_version": version}
        return client_version


class CardanoCollector():
    """A collector to fetch information about cardano RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id
        self.block_height_payload = {
            "id": "exporter",
            "jsonrpc": "2.0",
            "method": "queryNetwork/blockHeight"
        }
        self.interface = WebsocketInterface(
            url, **client_parameters)
        self.interface.daemon = None

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        return self.interface.cached_query(self.block_height_payload,
                                           skip_checks=True) is not None

    def block_height(self):
        """Returns latest block height."""
        return self.interface.cached_query(self.block_height_payload, skip_checks=True)

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency


class BitcoinCollector():
    """A collector to fetch information about Bitcoin RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))
        self._logger_metadata = {
            'component': 'BitcoinCollector',
            'url': strip_url(url)
        }
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

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rpc_post(self.network_info_payload) is not None

    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.blockchain_info_payload)
        return validate_dict_and_return_key_value(
            blockchain_info, 'blocks', self._logger_metadata)

    def total_difficulty(self):
        """Gets total difficulty from a previous call and clears the cache."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.blockchain_info_payload)
        return validate_dict_and_return_key_value(
            blockchain_info, 'difficulty', self._logger_metadata)

    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.network_info_payload)
        version = validate_dict_and_return_key_value(
            blockchain_info, 'version', self._logger_metadata, stringify=True)
        subversion = validate_dict_and_return_key_value(
            blockchain_info, 'subversion', self._logger_metadata, stringify=True)
        protocol_version = validate_dict_and_return_key_value(
            blockchain_info, 'protocolversion', self._logger_metadata, stringify=True)
        if version is None:
            return None
        client_version = {
            "client_version":
            f"version:{version} subversion:{subversion} protocolversion:{protocol_version}"}
        return client_version

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency


class FilecoinCollector():
    """A collector to fetch information about filecoin RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))
        self._logger_metadata = {
            'component': 'FilecoinCollector',
            'url': strip_url(url)
        }
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

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rpc_post(
            self.client_version_payload) is not None

    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.block_height_payload)
        return validate_dict_and_return_key_value(
            blockchain_info, 'Height', self._logger_metadata)

    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.client_version_payload)
        version = validate_dict_and_return_key_value(
            blockchain_info, 'Version', self._logger_metadata, stringify=True)
        api_version = validate_dict_and_return_key_value(
            blockchain_info, 'APIVersion', self._logger_metadata, stringify=True)
        if version is None:
            return None
        client_version = {
            "client_version": f"version:{version} APIversion:{api_version}"}
        return client_version

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency


class SolanaCollector():
    """A collector to fetch information about solana RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))
        self._logger_metadata = {
            'component': 'SolanaCollector',
            'url': strip_url(url)
        }
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

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rpc_post(
            self.client_version_payload) is not None

    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        return self.interface.cached_json_rpc_post(self.block_height_payload)

    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.interface.cached_json_rpc_post(
            self.client_version_payload)
        version = validate_dict_and_return_key_value(
            blockchain_info, 'solana-core', self._logger_metadata, stringify=True)
        if version is None:
            return None
        client_version = {"client_version": version}
        return client_version

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency


class StarknetCollector():
    """A collector to fetch information about starknet RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))

        self.block_height_payload = {
            "method": "starknet_blockNumber",
            "jsonrpc": "2.0",
            "id": 1
        }

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rpc_post(self.block_height_payload) is not None

    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        block_height = self.interface.cached_json_rpc_post(
            self.block_height_payload)
        return block_height

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency


class AptosCollector():
    """A collector to fetch information about Aptos endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))

        self._logger_metadata = {
            'component': 'AptosCollector',
            'url': strip_url(url)
        }

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rest_api_get() is not None

    def block_height(self):
        """Runs a cached query to return block height"""
        blockchain_info = self.interface.cached_json_rest_api_get()
        return validate_dict_and_return_key_value(
            blockchain_info, 'block_height', self._logger_metadata, to_number=True)

    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.interface.cached_json_rest_api_get()
        version = validate_dict_and_return_key_value(
            blockchain_info, 'git_hash', self._logger_metadata, stringify=True)
        if version is None:
            return None
        client_version = {"client_version": version}
        return client_version

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency

class TronCollector():
    """A collector to fetch information about Aptos endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                        client_parameters.get('ping_timeout'))

        self._logger_metadata = {
            'component': 'TronCollector',
            'url': strip_url(url)
        }
        self.client_version_payload = {
            'jsonrpc': '2.0',
            'method': "web3_clientVersion",
            'id': 1
        }
        self.block_height_payload = {
            'jsonrpc': '2.0',
            'method': "eth_blockNumber",
            'id': 1
        }

    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.interface.cached_json_rpc_post(
            self.client_version_payload) is not None

    def block_height(self):
        """Returns blockheight after converting string hexadecimal value to an int"""
        result = self.interface.cached_json_rpc_post(self.block_height_payload)

        if result and isinstance(result, str) and result.startswith('0x'):
            return int(result, 16)
        else:
            raise ValueError(f"Invalid block height result: {result}")

    def client_version(self):
        """Runs a cached query to return client version."""
        version = self.interface.cached_json_rpc_post(
            self.client_version_payload)
        if version is None:
            return None
        client_version = {"client_version": version}
        return client_version

    def latency(self):
        """Returns connection latency."""
        return self.interface.latest_query_latency
