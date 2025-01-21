"""Module for providing configuration"""

import os
import sys
import yaml
from schema import Schema, And, Optional, SchemaError, Regex
from log import logger


class Config():
    """Loads configuration yaml and validates it"""

    def __init__(self):
        self._logger = logger
        self._logger_metadata = {'component': 'Config'}
        self.configuration_file_path = os.getenv('CONFIG_FILE_PATH',
                                                 default='/config/config.yml')
        self._configuration = self._load_configuration()

    def get_property(self, property_name):
        """Gets a key from loaded configuration. Returns dynamic types.
        This should be fine since we know what to expect due to schema validation."""
        if property_name not in self._configuration:  # we don't want KeyError
            return None  # just return None if not found
        return self._configuration[property_name]

    @property
    def client_parameters(self):
        """Returns client parameters. In case none provided
        in the config, it returns pre-set values."""
        defaults_if_not_present = {
            'open_timeout': 7,
            'close_timeout': 3,
            'ping_interval': 10,
            'ping_timeout': 7
        }
        return self._configuration.get('connection_parameters',
                                       defaults_if_not_present)

    @property
    def endpoints(self):
        """Returns endpoints dict from the configuration."""
        return self.get_property('endpoints')

    def _load_configuration(self):
        supported_collectors = ('evm', 'evmhttp', 'cardano', 'conflux', 'solana',
                                'bitcoin', 'doge', 'filecoin', 'starknet', 'aptos',
                                'tron')

        configuration_schema = Schema({
            'blockchain':
            And(str),
            Optional('chain_id'):
            And(int),
            'network_name':
            And(str),
            'network_type':
            And(str, lambda s: s in ('Testnet', 'Mainnet')),
            'integration_maturity':
            And(str, lambda s: s in ('production', 'development')),
            'canonical_name':
            And(str),
            'chain_selector':
            And(int),
            'collector':
            And(str, lambda s: s in supported_collectors),
            Optional('connection_parameters'): {
                'open_timeout': And(int),
                'close_timeout': And(int),
                'ping_interval': And(int),
                'ping_timeout': And(int),
            },
            'endpoints': [{
                'url':
                And(str, Regex('https://.*|wss://.*|ws://.*')),
                'provider':
                And(str)
            }]
        })
        return self._load_and_validate(self.configuration_file_path,
                                       configuration_schema)

    def _load_and_validate(self, path: str, schema: Schema) -> dict:
        """Loads file from path as yaml and validates against provided schema."""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                yaml_object = yaml.load(file, Loader=yaml.SafeLoader)
                schema.validate(yaml_object)
                return yaml_object
        except (yaml.YAMLError, SchemaError, OSError) as error:
            self._logger.error("Error while loading yaml file.",
                               error=error,
                               path=path,
                               **self._logger_metadata)
            sys.exit(1)
