import os
import yaml
from schema import Schema, And, Use, Optional, SchemaError
import logging

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL, format='%(asctime)s - %(message)s')

config_schema = Schema({
    'blockchain':
    And(str, lambda s: s in allowed_chains),
    'chain_id':
    And(int),
    'network_name':
    And(str),
    'network_type':
    And(str, lambda s: s in ('Testnet', 'Mainnet')),
    'connection_timeout_seconds':
    And(int),
    'slo': {
        'max_pool_deviation_block_count': And(int),
        'max_response_latency_miliseconds': And(int)
    },
    'endpoints': [{
        'url': And(str),
        'provider': And(str, lambda s: s in allowed_providers)
    }]
})

validation_schema = Schema({
    'allowed_providers': [And(str)],
    'allowed_blockchains': [And(str)]
})

CONFIGURATION_FILE_PATH = os.getenv('CONFIG_FILE_PATH',
                                    default='/config/config.yml')
VALIDATION_FILE_PATH = os.getenv('VALIDATION_FILE_PATH',
                                 default='/config/validation.yml')
try:
    file = open(VALIDATION_FILE_PATH, 'r')
except IOError as e:
    logging.error("Problem with configuration file detected: {}".format(e))
    exit(1)
else:
    with file:
        try:
            validation_cfg = yaml.load(file, Loader=yaml.SafeLoader)
            validation_schema.validate(validation_cfg)
        except KeyError as e:
            logging.error(f"Failed to load key configuration: {e}")
            exit(1)
        except SchemaError as e:
            logging.error("Problem with configuration detected: {}".format(e))
            exit(1)

try:
    file = open(CONFIGURATION_FILE_PATH, 'r')
except IOError as e:
    logging.error("Problem with configuration file detected: {}".format(e))
    exit(1)
else:
    with file:
        try:
            cfg = yaml.load(file, Loader=yaml.SafeLoader)
            allowed_chains = validation_cfg['allowed_blockchains']
            allowed_providers = validation_cfg['allowed_providers']
            config_schema.validate(cfg)

            BLOCKCHAIN = cfg['blockchain']
            CHAIN_ID = cfg['chain_id']
            NETWORK_NAME = cfg['network_name']
            NETWORK_TYPE = cfg['network_type']
            RPCS = []
            RPCS.extend(cfg['endpoints'])

            TIMEOUT = cfg['connection_timeout_seconds']
            MAX_POOL_DEVIATION_BLOCK_COUNT = int(
                cfg['slo']['max_pool_deviation_block_count'])
            MAX_RESPONSE_LATENCY_MILISECONDS = int(
                cfg['slo']['max_response_latency_miliseconds'])
        except KeyError as e:
            logging.error(f"Failed to load key configuration: {e}")
            exit(1)
        except SchemaError as e:
            logging.error("Problem with configuration detected: {}".format(e))
            exit(1)
