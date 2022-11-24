import os
from typing import Optional
import yaml
from schema import Schema, And, SchemaError, Optional
import structlog

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
structlog.configure(processors=[structlog.processors.add_log_level, structlog.processors.JSONRenderer()])
logger = structlog.get_logger()


class configuration():

    def __init__(self, config_file_path: str, validation_file_path: str):
        self.allowed_providers = self._load_validation_file(validation_file_path)
        self.configuration = self._load_configuration_file(config_file_path)
        self.blockchain = self.configuration['blockchain']
        self.endpoints = self.configuration['endpoints']
        
        self._populate_endpoints_metadata()
        self._populate_chain_id_metadata()

        conn_defaults = {'open_timeout': 7, 'close_timeout': 3, 'response_timeout': 7, 'ping_interval': 10, 'ping_timeout': 7}
        self.connection_parameters = self.configuration.get('connection_parameters', conn_defaults)

        self.open_timeout = self.connection_parameters['open_timeout']
        self.close_timeout = self.connection_parameters['close_timeout']
        self.response_timeout = self.connection_parameters['response_timeout']
        self.ping_interval = self.connection_parameters['ping_interval']
        self.ping_timeout = self.connection_parameters['ping_timeout']

    def _populate_chain_id_metadata(self):
        # Conditionally add chain_id based on the colelctor type to each rpc item.
        if self.configuration['collector'] not in ['cardano', 'solana', 'bitcoin', 'doge', 'filecoin', 'starkware']:
            try:
                for endpoint in self.configuration['endpoints']:
                    endpoint['chain_id'] = self.configuration['chain_id']
            except KeyError:
                logger.error("This chain requires chain_id configuration, but it is not provided.")
    
    def _add_metadata_to_all_endpoints(self, key, value):
        for endpoint in self.endpoints:
            endpoint[key] = value

    def _populate_endpoints_metadata(self):
        """Iterates trough all of the """
        # Add blockchain, network_name and network_type metadata to each rpc item
        self._add_metadata_to_all_endpoints('blockchain', self.configuration['blockchain'])
        self._add_metadata_to_all_endpoints('network_type', self.configuration['network_type'])
        self._add_metadata_to_all_endpoints('network_name', self.configuration['network_name'])

    def _load_validation_file(self, path):
        logger.info('Loading {}'.format(path))
        validation_file_schema = Schema({'allowed_providers': [And(str)]})

        try:
            with open(path, 'r') as file:
                validation_cfg = yaml.load(file, Loader=yaml.SafeLoader)
                validation_file_schema.validate(validation_cfg)
                allowed_providers = validation_cfg['allowed_providers']
                return allowed_providers
        except KeyError as e:
            logger.error(f'Failed to load key configuration: {e}')
            exit(1)
        except (SchemaError, IOError) as e:
            logger.error('Problem with configuration detected: {}'.format(e))
            exit(1)

    def isEvm(self) -> bool:
        return self.configuration['collector'] == "evm"

    def isSolana(self) -> bool:
        return self.configuration['collector'] == "solana"

    def isCardano(self) -> bool:
        return self.configuration['collector'] == "cardano"

    def isConflux(self) -> bool:
        return self.configuration['collector'] == "conflux"

    def isBitcoin(self) -> bool:
        return self.configuration['collector'] == "bitcoin"

    def isDoge(self) -> bool:
        return self.configuration['collector'] == "doge"

    def isFilecoin(self) -> bool:
        return self.configuration['collector'] == "filecoin"

    def isStarkware(self) -> bool:
        return self.configuration['collector'] == "starkware"

    def _load_configuration_file(self, path):
        logger.info('Loading {}'.format(path))
        configuration_file_schema = Schema({
            'blockchain':
            And(str),
            Optional('chain_id'):
            And(int),
            'network_name':
            And(str),
            'network_type':
            And(str, lambda s: s in ('Testnet', 'Mainnet')),
            'collector':
            And(str, lambda s: s in
                ('evm', 'cardano', 'conflux', 'solana', 'bitcoin', 'doge', 'filecoin', 'starkware')),
            Optional('connection_parameters'): {
                'open_timeout': And(int),
                'close_timeout': And(int),
                'response_timeout': And(int),
                'ping_interval': And(int),
                'ping_timeout': And(int),
            },
            'endpoints': [{
                'url':
                And(str),
                # Solana specific field since solana collector uses both https and wss endpoints for probing.
                Optional('subscribe_url'):
                And(str),
                'provider':
                And(str, lambda s: s in self.allowed_providers)
            }]
        })
        try:
            with open(path, 'r') as file:
                validation_cfg = yaml.load(file, Loader=yaml.SafeLoader)
                configuration_file_schema.validate(validation_cfg)
                return validation_cfg
        except KeyError as e:
            logger.error(f'Failed to load key configuration: {e}')
            exit(1)
        except (SchemaError, IOError) as e:
            logger.error('Problem with configuration detected: {}'.format(e))
            exit(1)