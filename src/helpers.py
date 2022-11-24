
import os
import urllib.parse
import json
from settings import configuration

# Configuration
cfg_file_path = os.getenv('CONFIG_FILE_PATH', default='/config/config.yml')
valid_file_path = os.getenv('VALIDATION_FILE_PATH', default='/config/validation.yml')
cfg = configuration(cfg_file_path, valid_file_path)


# Random functions
def strip_url(url):
    """Returns a stripped url from all parameters, usernames or passwords if present.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname


def generate_labels_from_metadata(rpc_metadata):
    """This function returns a fixed dict `labels` which never changes, these will eventually become prometheus labels.
    In addition, it takes rpc_metadata dict, and extracts values for each of the static labels."""

    labels = ['url', 'provider', 'blockchain', 'network_name', 'network_type']
    label_values = [
        rpc_metadata['url'], rpc_metadata['provider'], rpc_metadata['blockchain'], rpc_metadata['network_name'],
        rpc_metadata['network_type']
    ]

    if "chain_id" in rpc_metadata:
        labels.append("evmChainID")
        label_values.append(str(rpc_metadata['chain_id']))

    return labels, label_values


def hex_to_int(hex_value):
    return int(hex_value, 16)


def key_from_json_str(json_body, key):
    return json.loads(json_body)[key]
