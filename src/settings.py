import os
from typing import Optional
import yaml
from schema import Schema, And, SchemaError, Optional
import logging

logger = logging.getLogger('exporter')
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

logging.basicConfig(level=LOGLEVEL,
                    format="{'thread': '%(threadName)s', 'level': '%(levelname)s', 'message': '%(message)s'}")


class configuration():

    def __init__(self, config_file_path: str, validation_file_path: str):
        self.allowed_providers = self._load_validation_file(validation_file_path)
        self.configuration = self._load_configuration_file(config_file_path)
        self.blockchain = self.configuration['blockchain']
        # Load chain_id only if evm compatible collector
        if self.configuration['collector'] not in ['cardano', 'solana', 'bitcoin', 'doge']:
            try:
                self.chain_id = self.configuration['chain_id']
            except KeyError:
                logger.error("This chain requires chain_id configuration, but it is not provided.")
        self.network_type = self.configuration['network_type']
        self.network_name = self.configuration['network_name']
        self.endpoints = self.configuration['endpoints']
        try:
            self.open_timeout = self.configuration['connection_parameters']['open_timeout']
        except KeyError:
            self.open_timeout = 3
        try:
            self.close_timeout = self.configuration['connection_parameters']['close_timeout']
        except KeyError:
            self.close_timeout = 1
        try:
            self.response_timeout = self.configuration['connection_parameters']['response_timeout']
        except KeyError:
            self.response_timeout = 3
        try:
            self.ping_interval = self.configuration['connection_parameters']['ping_interval']
        except KeyError:
            self.ping_interval = 6
        try:
            self.ping_timeout = self.configuration['connection_parameters']['ping_timeout']
        except KeyError:
            self.ping_timeout = 2

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
            And(str, lambda s: s in ('evm', 'cardano', 'conflux', 'solana', 'bitcoin', 'doge')),
            Optional('connection_parameters'): {
                Optional('open_timeout'): And(int),
                Optional('close_timeout'): And(int),
                Optional('response_timeout'): And(int),
                Optional('ping_interval'): And(int),
                Optional('ping_timeout'): And(int),
            },
            'endpoints': [{
                Optional('ws_url'): And(str),
                Optional('https_url'): And(str),
                'provider': And(str, lambda s: s in self.allowed_providers)
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


cfg_file_path = os.getenv('CONFIG_FILE_PATH', default='/config/config.yml')
valid_file_path = os.getenv('VALIDATION_FILE_PATH', default='/config/validation.yml')

cfg = configuration(cfg_file_path, valid_file_path)
