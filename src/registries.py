"""A module that providers registries of objects."""
import sys

from configuration import Config
import collectors
from log import logger


class Endpoint():  # pylint: disable=too-few-public-methods
    """RPC Endpoint class, to store metadata."""

    def __init__(  # pylint: disable=too-many-arguments
            self, url, provider, blockchain, network_name, network_type,
            chain_id, **client_parameters):
        self.url = url
        self.chain_id = chain_id
        self.labels = [
            url, provider, blockchain, network_name, network_type,
            str(chain_id)
        ]
        self.client_parameters = client_parameters


class EndpointRegistry(Config):
    """A registry of all endpoints."""

    def __init__(self):
        super().__init__()
        self._logger = logger
        self._logger_metadata = {'component': 'Registries'}

    @property
    def blockchain(self):
        """Returns blockchain as a lowercase string."""
        return self.get_property('blockchain').lower()

    @property
    def collector(self):
        """Returns type of collector used as a lowercase string."""
        return self.get_property('collector').lower()

    @property
    def get_endpoint_registry(self) -> list:
        """Iterates trough all of the endpoints and instantiates
        them as Endpoints class in a dict. Returns the populated dict."""
        endpoints_list = []
        for item in self.endpoints:
            endpoints_list.append(
                Endpoint(item['url'], item['provider'],
                         self.blockchain,
                         self.get_property('network_name'),
                         self.get_property('network_type'),
                         self.get_property('chain_id'),
                         **self.client_parameters))
        return endpoints_list


class CollectorRegistry(EndpointRegistry):
    """A registry of all collectors."""

    @property
    def get_collector_registry(self) -> list:
        """Iterates trough all of the instantiated endpoints and loads
        proper collector type based on the collector and chain name."""
        collectors_list = []

        for item in self.get_endpoint_registry:
            collector = None
            match self.collector, self.blockchain:
                case "conflux", "conflux":
                    collector = collectors.ConfluxCollector
                case "cardano", "cardano":
                    collector = collectors.CardanoCollector
                case "bitcoin", "bitcoin":
                    collector = collectors.BitcoinCollector
                case "bitcoin", "dogecoin":
                    collector = collectors.BitcoinCollector
                case "filecoin", "filecoin":
                    collector = collectors.FilecoinCollector
                case "solana", "solana":
                    collector = collectors.SolanaCollector
                case "starknet", "starknet":
                    collector = collectors.StarknetCollector
                case "aptos", "aptos":
                    collector = collectors.AptosCollector
                case "evm", other:  # pylint: disable=unused-variable
                    collector = collectors.EvmCollector
            if collector is None:
                self._logger.error("Endpoint has no supported collector",
                                   collector=self.collector,
                                   blockchain=self.blockchain,
                                   **self._logger_metadata)
                sys.exit(1)
            else:
                collectors_list.append(collector(item.url,
                                                 item.labels, item.chain_id,
                                                 **self.client_parameters))
        return collectors_list
