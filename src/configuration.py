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
        validation_file_path = os.getenv('VALIDATION_FILE_PATH',
                                         default='/config/validation.yml')
        validation_schema = Schema({'allowed_providers': [And(str)]})
        valid_providers = self.load_and_validate(
            validation_file_path, validation_schema)['allowed_providers']

        configuration_file_path = os.getenv('CONFIG_FILE_PATH',
                                            default='/config/config.yml')
        supported_collectors = ('evm', 'cardano', 'conflux', 'solana',
                                'bitcoin', 'doge', 'filecoin', 'starkware')
        configuration_schema = Schema({
            'blockchain':
            And(str),
            Optional('chain_id'):
            And(int),
            'network_name':
            And(str),
            'network_type':
            And(str, lambda s: s in ('Testnet', 'Mainnet')),
            'collector':
            And(str, lambda s: s in supported_collectors),
            Optional('open_timeout'):
            And(int),
            Optional('close_timeout'):
            And(int),
            Optional('ping_interval'):
            And(int),
            Optional('ping_timeout'):
            And(int),
            'endpoints': [{
                'url': And(str, Regex('https://.*|wss://.*')),
                'provider': And(str, lambda s: s in valid_providers)
            }]
        })
        self._config = self.load_and_validate(configuration_file_path,
                                              configuration_schema)
        self._logger = logger
        self._logger_metadata = {
            'component': 'Config',
            'configuration_file_path': configuration_file_path,
            'validation_file_path': validation_file_path
        }

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
        return self._config.get('connection_parameters',
                                defaults_if_not_present)

    @property
    def endpoints(self):
        """Returns endpoints dict from the configuration."""
        return self.get_property('endpoints')

    def get_property(self, property_name):
        """Gets a key from loaded configuration. Returns dynamic types.
        This should be fine since we know what to expect due to schema validation."""
        if property_name not in self._config.keys():  # we don't want KeyError
            return None  # just return None if not found
        return self._config[property_name]

    def load_and_validate(self, path: str, schema: Schema) -> dict:
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
