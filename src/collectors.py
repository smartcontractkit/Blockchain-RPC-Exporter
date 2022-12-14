"""Module for providing interfaces to interact with https and websocket RPC endpoints."""
from interfaces import WebsocketInterface, HttpsInterface


class EvmCollector(WebsocketInterface):
    """A collector to fetch information about evm compatible RPC endpoints."""

    # We only override __getattr__ method for collectors that do not implement all attributes.
    # (alive, disconnects, heads_received, block_height, client_version, total_difficulty)
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id

        sub_payload = {
            "method": 'eth_subscribe',
            "jsonrpc": "2.0",
            "id": chain_id,
            "params": ["newHeads"]
        }
        super().__init__(url, sub_payload, **client_parameters)
        self.daemon = True
        self.start()

    @property
    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.healthy

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.get_message_property_to_hex('number')

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "web3_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        return self.cached_query(payload)


class ConfluxCollector(WebsocketInterface):
    """A collector to fetch information about conflux RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id

        sub_payload = {
            "method": 'cfx_subscribe',
            "jsonrpc": "2.0",
            "id": chain_id,
            "params": ["newHeads"]
        }
        super().__init__(url, sub_payload, **client_parameters)
        self.daemon = True
        self.start()

    @property
    def alive(self):
        """Returns if the websocket subscription is healthy."""
        return self.healthy

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.get_message_property_to_hex('height')

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        payload = {
            "jsonrpc": "2.0",
            "method": "cfx_clientVersion",
            "params": [],
            "id": self.chain_id
        }
        return self.cached_query(payload)


class CardanoCollector(WebsocketInterface):
    """A collector to fetch information about conflux RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):
        self.labels = labels
        self.chain_id = chain_id
        super().__init__(url, None, **client_parameters)

    @property
    def alive(self):
        """Returns true if endpoint is alive, false if not."""
        return self.cached_query(self.block_height_payload,
                                 skip_checks=True) is not None

    @property
    def block_height(self):
        """Returns latest block height."""
        return self.query(self.block_height_payload, skip_checks=True)


class BitcoinCollector(HttpsInterface):
    """A collector to fetch information about Bitcoin RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        super().__init__(url, client_parameters.get('open_timeout'),
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
        return self.cached_json_rpc_post(self.network_info_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        return self.cached_json_rpc_post(
            self.blockchain_info_payload)['blocks']

    @property
    def total_difficulty(self):
        """Gets total difficulty from a previous call and clears the cache."""
        total_difficulty = self.cached_json_rpc_post(
            self.blockchain_info_payload, invalidate_cache=True)['difficulty']
        return total_difficulty


    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        version = str(
            self.cached_json_rpc_post(self.network_info_payload, invalidate_cache=True)['version'])
        return version

class FilecoinCollector(HttpsInterface):
    """A collector to fetch information about conflux RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        super().__init__(url, client_parameters.get('open_timeout'),
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
        return self.cached_json_rpc_post(
            self.client_version_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        return self.cached_json_rpc_post(self.block_height_payload)['Height']

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        version = str(
            self.cached_json_rpc_post(self.client_version_payload)['Version'])
        self.cache.remove_key_from_cache(self.client_version_payload)
        return version


class SolanaCollector(HttpsInterface):
    """A collector to fetch information about conflux RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        super().__init__(url, client_parameters.get('open_timeout'),
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
        return self.cached_json_rpc_post(
            self.client_version_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        return self.cached_json_rpc_post(self.block_height_payload)

    @property
    def client_version(self):
        """Runs a cached query to return client version."""
        version = str(
            self.cached_json_rpc_post(
                self.client_version_payload)['solana-core'])
        self.cache.remove_key_from_cache(self.client_version_payload)
        return version


class StarkwareCollector(HttpsInterface):
    """A collector to fetch information about conflux RPC endpoints."""

    # Override __getattr_ since we don't have all metrics implemented for our registry.
    def __getattr__(self, name):
        return None

    def __init__(self, url, labels, chain_id, **client_parameters):

        self.labels = labels
        self.chain_id = chain_id
        super().__init__(url, client_parameters.get('open_timeout'),
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
        return self.cached_json_rpc_post(self.block_height_payload) is not None

    @property
    def block_height(self):
        """Returns latest block height. Cache is cleared when total_difficulty is fetched.
        In order for this collector to work, alive and block_height calls need to be
        followed with total_difficulty and client_version calls so the cache is cleared."""
        block_height = self.cached_json_rpc_post(self.block_height_payload)
        self.cache.remove_key_from_cache(self.block_height_payload)
        return block_height
