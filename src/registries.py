"""A module that providers registries of objects."""
from configuration import Config
import collectors


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

    @property
    def blockchain(self):
        """Returns blockchain."""
        return self.get_property('blockchain')

    @property
    def collector(self):
        """Returns type of collector used."""
        return self.get_property('collector')

    @property
    def get_endpoint_registry(self) -> list:
        """Iterates trough all of the endpoints and instantiates
        them as Endpoints class in a dict. Returns the populated dict."""
        endpoints_list = []
        for item in self.endpoints:
            endpoints_list.append(
                Endpoint(item['url'], item['provider'],
                         self.get_property('blockchain'),
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
                case "evm", "conflux":
                    collector = collectors.ConfluxCollector
                case "cardano", "cardano":
                    collector = collectors.CardanoCollector
                case "bitcoin", "bitcoin":
                    collector = collectors.BitcoinCollector
                case "filecoin", "filecoin":
                    collector = collectors.FilecoinCollector
                case "solana", "solana":
                    collector = collectors.SolanaCollector
                case "starkware", "starkware":
                    collector = collectors.StarkwareCollector
                case "evm", other:  # pylint: disable=unused-variable
                    collector = collectors.EvmCollector
            if collector is None:
                # TODO log this error properly
                self._logger.error(
                    f"collector: {self.collector} on bloackchain: {self.blockchain} not found"
                )
            else:
                collectors_list.append(collector(item.url,
                                                 item.labels, item.chain_id,
                                                 **self.client_parameters))
        return collectors_list
