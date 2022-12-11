"""A module that providers registries of objects."""
from configuration import Config
import collectors


class Endpoint():  #pylint: disable=too-few-public-methods
    """RPC Endpoint class, to store metadata."""

    def __init__(  #pylint: disable=too-many-arguments
            self,
            url,
            provider,
            blockchain,
            network_name,
            network_type,
            chain_id,
            **client_parameters):
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
    def get_endpoint_registry(self) -> dict:
        """Iterates trough all of the endpoints and instantiates
        them as Endpoints class in a dict. Returns the populated dict."""
        return_dict = []
        for item in self.endpoints:
            return_dict.append(
                Endpoint(item['url'], item['provider'],
                         self.get_property('blockchain'),
                         self.get_property('network_name'),
                         self.get_property('network_type'),
                         self.get_property('chain_id'),
                         **self.client_parameters))
        return return_dict


class CollectorRegistry(EndpointRegistry):
    """A registry of all collectors."""

    @property
    def get_collector_registry(self) -> dict:
        """Iterates trough all of the instantiated endpoints and loads
        proper collector type based on the collector and chain name."""
        return_dict = []

        for item in self.get_endpoint_registry:
            match self.collector, self.blockchain:
                case "evm", "conflux":
                    return_dict.append(
                                collectors.ConfluxCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "cardano", "cardano":
                    return_dict.append(
                                collectors.CardanoCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "bitcoin", "bitcoin":
                    return_dict.append(
                                collectors.BitcoinCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "filecoin", "filecoin":
                    return_dict.append(
                                collectors.FilecoinCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "solana", "solana":
                    return_dict.append(
                                collectors.SolanaCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "starkware", "starkware":
                    return_dict.append(
                                collectors.StarkwareCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
                case "evm", other: ##pylint: disable=unused-variable
                    return_dict.append(
                                collectors.EvmCollector(item.url,
                                item.labels, item.chain_id,
                                **self.client_parameters))
        return return_dict
