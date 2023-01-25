"""Module for providing interfaces to interact with https and websocket RPC endpoints."""
from interfaces import WebsocketInterface, HttpsInterface


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
        self.websocket = WebsocketInterface(
            url, sub_payload, **client_parameters)
        self.websocket.daemon = True
        self.websocket.start()

    @property
    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.websocket.healthy

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.websocket.get_message_property_to_hex('number')

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        return self.websocket.cached_query(payload)


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
        self.websocket = WebsocketInterface(
            url, sub_payload, **client_parameters)
        self.websocket.daemon = True
        self.websocket.start()

    @property
    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.websocket.healthy

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.websocket.get_message_property_to_hex('height')

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "cfx_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        return self.websocket.cached_query(payload)


class CardanoCollector():
    """A collector to fetch information about cardano RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id
        self.block_height_payload = {
            "type": "jsonwsp/request",
            "version": "1.0",
            "servicename": "ogmios",
            "methodname": "Query",
            "args": {
                "query": "blockHeight"
            }
        }
        self.websocket = WebsocketInterface(
            url, **client_parameters)
        self.websocket.daemon = None

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        return self.websocket.cached_query(self.block_height_payload,
                                           skip_checks=True) is not None

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.websocket.query(self.block_height_payload, skip_checks=True)


class BitcoinCollector():
    """A collector to fetch information about Bitcoin RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.https_interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                              client_parameters.get('ping_timeout'))

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

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.https_interface.cached_json_rpc_post(self.network_info_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.blockchain_info_payload)
        if isinstance(blockchain_info, dict):
            return blockchain_info.get('blocks')
        return None

    @property
    def total_difficulty(self):
        """Gets total difficulty from a previous call and clears the cache."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.blockchain_info_payload, invalidate_cache=True)
        if isinstance(blockchain_info, dict):
            return blockchain_info.get('difficulty')
        return None

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.network_info_payload, invalidate_cache=True)
        if isinstance(blockchain_info, dict):
            version = blockchain_info.get('version')
            if version is not None:
                return str(version)
        return None


class FilecoinCollector():
    """A collector to fetch information about filecoin RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.https_interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                              client_parameters.get('ping_timeout'))

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

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.https_interface.cached_json_rpc_post(
            self.client_version_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.block_height_payload)
        if isinstance(blockchain_info, dict):
            return blockchain_info.get('Height')
        return None

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.client_version_payload, invalidate_cache=True)
        if isinstance(blockchain_info, dict):
            version = blockchain_info.get('Version')
            if version is not None:
                return str(version)
        return None


class SolanaCollector():
    """A collector to fetch information about solana RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.https_interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                              client_parameters.get('ping_timeout'))

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

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.https_interface.cached_json_rpc_post(
            self.client_version_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        return self.https_interface.cached_json_rpc_post(self.block_height_payload)

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        blockchain_info = self.https_interface.cached_json_rpc_post(
            self.client_version_payload, invalidate_cache=True)
        if isinstance(blockchain_info, dict):
            version = blockchain_info.get('solana-core')
            if version is not None:
                return str(version)
        return None


class StarkwareCollector():
    """A collector to fetch information about starkware RPC endpoints."""

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        self.https_interface = HttpsInterface(url, client_parameters.get('open_timeout'),
                                              client_parameters.get('ping_timeout'))

        self.block_height_payload = {
            "method": "starknet_blockNumber",
            "jsonrpc": "2.0",
            "id": 1
        }

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        # Run cached query because we can also fetch client version from this
        # later on. This will save us an RPC call per run.
        return self.https_interface.cached_json_rpc_post(self.block_height_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        block_height = self.https_interface.cached_json_rpc_post(
            self.block_height_payload, invalidate_cache=True)
        return block_height
