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
        self._populate_endpoints_metadata()
        self._populate_chain_id_metadata()
        self.blockchain = self.configuration['blockchain']
        self.endpoints = self.configuration['endpoints']

        try:
            self.open_timeout = self.configuration['connection_parameters']['open_timeout']
        except KeyError:
            self.open_timeout = 7
            logger.info(f"connection_parameters.open_timeout not set, defaulting to {self.open_timeout}")
        try:
            self.close_timeout = self.configuration['connection_parameters']['close_timeout']
        except KeyError:
            self.close_timeout = 3
            logger.info(f"connection_parameters.close_timeout not set, defaulting to {self.close_timeout}")
        try:
            self.response_timeout = self.configuration['connection_parameters']['response_timeout']
        except KeyError:
            self.response_timeout = 7
            logger.info(f"connection_parameters.response_timeout not set, defaulting to {self.response_timeout}")
        try:
            self.ping_interval = self.configuration['connection_parameters']['ping_interval']
        except KeyError:
            self.ping_interval = 10
            logger.info(f"connection_parameters.ping_interval not set, defaulting to {self.ping_interval}")
        try:
            self.ping_timeout = self.configuration['connection_parameters']['ping_timeout']
        except KeyError:
            self.ping_timeout = 7
            logger.info(f"connection_parameters.ping_timeout not set, defaulting to {self.ping_timeout}")

    def _populate_chain_id_metadata(self):
        # Conditionally add chain_id based on the colelctor type to each rpc item.
        if self.configuration['collector'] not in ['cardano', 'solana', 'bitcoin', 'doge', 'filecoin', 'starkware']:
            try:
                for endpoint in self.configuration['endpoints']:
                    endpoint['chain_id'] = self.configuration['chain_id']
            except KeyError:
                logger.error("This chain requires chain_id configuration, but it is not provided.")

    def _populate_endpoints_metadata(self):
        """Iterates trough all of the """
        # Add blockchain, network_name and network_type metadata to each rpc item
        for endpoint in self.configuration['endpoints']:
            endpoint['blockchain'] = self.configuration['blockchain']
            endpoint['network_type'] = self.configuration['network_type']
            endpoint['network_name'] = self.configuration['network_name']

    def _load_validation_file(self, path):
        logger.info('Loading {}'.format(path))
        validation_file_schema = Schema({'allowed_providers': [And(str)]})

        try:
            file = self._load_file(path)
            validation_cfg = yaml.load(file, Loader=yaml.SafeLoader)
            validation_file_schema.validate(validation_cfg)
            allowed_providers = validation_cfg['allowed_providers']
            return allowed_providers
        except KeyError as e:
            logger.error(f'Failed to load key configuration: {e}')
            exit(1)
        except SchemaError as e:
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
                Optional('open_timeout'): And(int),
                Optional('close_timeout'): And(int),
                Optional('response_timeout'): And(int),
                Optional('ping_interval'): And(int),
                Optional('ping_timeout'): And(int),
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
            file = self._load_file(path)
            validation_cfg = yaml.load(file, Loader=yaml.SafeLoader)
            configuration_file_schema.validate(validation_cfg)
            return validation_cfg
        except KeyError as e:
            logger.error(f'Failed to load key configuration: {e}')
            exit(1)
        except SchemaError as e:
            logger.error('Problem with configuration detected: {}'.format(e))
            exit(1)

    def _load_file(self, path):
        try:
            file = open(path, 'r')
            logger.info('Validating {}'.format(path))
            return file
        except IOError as e:
            logger.error('Problem with configuration file detected: {}'.format(e))
            exit(1)
